# FastAPI Modern Web Backend for Stem Separator Studio

import os
import sys
import json
import zipfile
import io
import asyncio
import threading
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Header, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.hardware import detect_hardware
from core.models_config import PRESETS, AVAILABLE_MODELS, STEM_LABELS
from core.pipeline import SeparationPipeline
from core.dialogs import pick_audio_file, pick_folder

# Stdout protection
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR = PROJECT_ROOT / "web" / "static"

app = FastAPI(title="Stem Separator Studio API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
connected_websockets: List[WebSocket] = []
main_event_loop: Optional[asyncio.AbstractEventLoop] = None

current_job: Dict[str, Any] = {
    "status": "idle",
    "percent": 0.0,
    "stage": "Listo. Seleccioná una canción para comenzar.",
    "chunk": 0,
    "total_chunks": 0,
    "elapsed": "",
    "eta": "",
    "logs": [],
    "stems": [],
    "output_dir": None,
    "input_file": None
}

class SeparateRequest(BaseModel):
    input_file: str
    output_dir: Optional[str] = None
    preset_key: str = "full_multitrack"
    format: str = "WAV"
    quality: str = "fast"
    custom_stems: Optional[List[str]] = None

@app.on_event("startup")
async def on_startup():
    global main_event_loop
    main_event_loop = asyncio.get_running_loop()

def broadcast_event(event: Dict[str, Any]):
    """Thread-safe real-time WebSocket broadcast."""
    global current_job

    event_type = event.get("type")
    if event_type == "progress":
        current_job["percent"] = event.get("percent", current_job["percent"])
        current_job["stage"] = event.get("stage", current_job["stage"])
        current_job["chunk"] = event.get("chunk", current_job["chunk"])
        current_job["total_chunks"] = event.get("total_chunks", current_job["total_chunks"])
        current_job["elapsed"] = event.get("elapsed", current_job["elapsed"])
        current_job["eta"] = event.get("eta", current_job["eta"])
    elif event_type == "log":
        msg = event.get("message", "")
        current_job["logs"].append(msg)
        if len(current_job["logs"]) > 300:
            current_job["logs"] = current_job["logs"][-300:]
    elif event_type == "completed":
        current_job["status"] = "completed"
        current_job["percent"] = 100.0
        current_job["stage"] = "¡Separación completada con éxito!"
        current_job["stems"] = event.get("stems", [])
        current_job["output_dir"] = event.get("output_dir")
    elif event_type == "error":
        current_job["status"] = "error"
        current_job["stage"] = f"Error: {event.get('message')}"

    async def _send():
        dead = []
        msg = json.dumps(event)
        for ws in connected_websockets:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        for d in dead:
            if d in connected_websockets:
                connected_websockets.remove(d)

    if main_event_loop and main_event_loop.is_running():
        asyncio.run_coroutine_threadsafe(_send(), main_event_loop)

@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.append(websocket)
    hw = detect_hardware()
    await websocket.send_text(json.dumps({"type": "hardware", "data": hw}))
    await websocket.send_text(json.dumps({"type": "state", "data": current_job}))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)

@app.get("/api/status")
def get_status():
    return {
        "job": current_job,
        "hardware": detect_hardware()
    }

@app.get("/api/hardware")
def get_hardware():
    return detect_hardware()

@app.get("/api/presets")
def get_presets():
    return {
        "presets": PRESETS,
        "models": AVAILABLE_MODELS,
        "stem_labels": STEM_LABELS
    }

@app.post("/api/browse-file")
def browse_file():
    """Opens native OS file explorer dialog safely without Tkinter."""
    file_path = pick_audio_file()
    if file_path:
        p = Path(file_path).resolve()
        default_out = str(p.parent / f"{p.stem}_Stems")
        return {"file_path": str(p), "filename": p.name, "default_output_dir": default_out}
    return {"file_path": None}

@app.post("/api/browse-folder")
def browse_folder():
    """Opens native OS folder picker dialog safely without Tkinter."""
    folder_path = pick_folder()
    if folder_path:
        p = Path(folder_path).resolve()
        return {"folder_path": str(p)}
    return {"folder_path": None}

@app.post("/api/open-folder")
def open_folder(data: Dict[str, str]):
    folder_path = data.get("folder_path") or current_job.get("output_dir")
    if folder_path and Path(folder_path).exists():
        try:
            if sys.platform == "win32":
                os.startfile(folder_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    return {"success": False, "error": "Carpeta no encontrada"}

@app.get("/api/audio/{filename}")
def stream_audio(filename: str, request: Request, range: Optional[str] = Header(None)):
    """
    HTTP 206 Partial Content range-aware audio streaming for instant seek and scrubbing.
    """
    out_dir_str = current_job.get("output_dir")
    if not out_dir_str:
        raise HTTPException(status_code=404, detail="No active output directory")

    file_path = Path(out_dir_str) / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo de audio no encontrado")

    file_size = file_path.stat().st_size
    media_type = "audio/wav" if filename.endswith(".wav") else "audio/mpeg"

    if range is not None:
        parts = range.replace("bytes=", "").split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
        end = min(end, file_size - 1)
        chunk_size = end - start + 1

        def iter_file():
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = chunk_size
                while remaining > 0:
                    read_bytes = min(remaining, 64 * 1024)
                    data = f.read(read_bytes)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": media_type,
        }
        return StreamingResponse(iter_file(), status_code=206, headers=headers)

    return FileResponse(path=str(file_path), media_type=media_type, filename=filename)

@app.get("/api/download-zip")
def download_all_zip():
    """Packages all generated stems into a ZIP file for one-click download."""
    out_dir_str = current_job.get("output_dir")
    if not out_dir_str or not Path(out_dir_str).exists():
        raise HTTPException(status_code=404, detail="No hay archivos generados para descargar")

    out_path = Path(out_dir_str)
    audio_files = [p for p in out_path.iterdir() if p.is_file() and p.suffix.lower() in [".wav", ".mp3", ".flac", ".m4a"]]
    if not audio_files:
        raise HTTPException(status_code=404, detail="No se encontraron stems de audio en la carpeta")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for f in audio_files:
            zip_file.write(f, arcname=f.name)

    zip_buffer.seek(0)
    zip_name = f"{out_path.name}.zip"
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_name}"'}
    )

@app.post("/api/separate")
def start_separation(req: SeparateRequest):
    global current_job

    input_path = Path(req.input_file).resolve()
    if not input_path.exists():
        raise HTTPException(status_code=400, detail="El archivo de audio no existe")

    output_dir = req.output_dir or str(input_path.parent / f"{input_path.stem}_Stems")
    out_path = Path(output_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    preset_info = PRESETS.get(req.preset_key, PRESETS["full_multitrack"])
    model_key = preset_info["model_key"]
    overlap = 4 if req.quality == "high" else 2

    # Reset job state
    current_job["status"] = "processing"
    current_job["percent"] = 1.0
    current_job["stage"] = f"Iniciando separación con {preset_info['title']}..."
    current_job["chunk"] = 0
    current_job["total_chunks"] = 0
    current_job["elapsed"] = ""
    current_job["eta"] = ""
    current_job["logs"] = [f"Iniciando trabajo para: {input_path.name}"]
    current_job["stems"] = []
    current_job["output_dir"] = str(out_path)
    current_job["input_file"] = str(input_path)

    broadcast_event({
        "type": "state",
        "data": current_job
    })

    def _worker():
        try:
            pipeline = SeparationPipeline(
                models_dir=MODELS_DIR,
                event_callback=broadcast_event
            )
            pipeline.process(
                input_file=str(input_path),
                output_dir=str(out_path),
                model_key=model_key,
                output_format=req.format,
                overlap=overlap
            )
        except Exception as e:
            broadcast_event({"type": "error", "message": str(e)})

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()

    return {"status": "started", "output_dir": str(out_path)}

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        return FileResponse(index_file, headers=headers)
    return HTMLResponse("<h1>Stem Separator Studio</h1>")
