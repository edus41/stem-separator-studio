# FastAPI Modern Web Backend for Stem Separator Studio

import os
import sys
import json
import asyncio
import threading
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.hardware import detect_hardware
from core.models_config import PRESETS, AVAILABLE_MODELS, STEM_LABELS
from core.pipeline import SeparationPipeline

# Stdout protection
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR = PROJECT_ROOT / "web" / "static"

app = FastAPI(title="Stem Separator Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
connected_websockets: List[WebSocket] = []
current_output_dir: Optional[Path] = None

class SeparateRequest(BaseModel):
    input_file: str
    output_dir: Optional[str] = None
    preset_key: str = "vocals_inst"
    format: str = "WAV"
    quality: str = "fast"
    custom_stems: Optional[List[str]] = None

def broadcast_event(event: Dict[str, Any]):
    """Send real-time event to all connected web clients via WebSockets."""
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

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(_send(), loop)
        else:
            asyncio.run(_send())
    except Exception:
        pass

@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.append(websocket)
    # Send initial hardware info
    hw = detect_hardware()
    await websocket.send_text(json.dumps({"type": "hardware", "data": hw}))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)

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
    """Opens native OS file explorer dialog."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de música",
            filetypes=[
                ("Archivos de audio", "*.mp3 *.wav *.flac *.m4a *.ogg *.aac *.wma"),
                ("Todos los archivos", "*.*")
            ]
        )
        root.destroy()
        if file_path:
            p = Path(file_path)
            default_out = str(p.parent / f"{p.stem}_Stems")
            return {"file_path": file_path, "filename": p.name, "default_output_dir": default_out}
        return {"file_path": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/browse-folder")
def browse_folder():
    """Opens native OS folder picker dialog."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder_path = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        root.destroy()
        return {"folder_path": folder_path or None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/open-folder")
def open_folder(data: Dict[str, str]):
    folder_path = data.get("folder_path")
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
def stream_audio(filename: str):
    global current_output_dir
    if current_output_dir:
        file_path = current_output_dir / filename
        if file_path.exists():
            return FileResponse(
                path=str(file_path),
                media_type="audio/wav" if filename.endswith(".wav") else "audio/mpeg",
                filename=filename
            )
    raise HTTPException(status_code=404, detail="Audio file not found")

@app.post("/api/separate")
def start_separation(req: SeparateRequest):
    global current_output_dir
    input_path = Path(req.input_file)
    if not input_path.exists():
        raise HTTPException(status_code=400, detail="El archivo de audio no existe")

    output_dir = req.output_dir or str(input_path.parent / f"{input_path.stem}_Stems")
    current_output_dir = Path(output_dir)

    preset_info = PRESETS.get(req.preset_key, PRESETS["vocals_inst"])
    model_key = preset_info["model_key"]
    overlap = 4 if req.quality == "high" else 2

    # Execute in background thread so HTTP response returns immediately
    def _worker():
        try:
            pipeline = SeparationPipeline(
                models_dir=MODELS_DIR,
                event_callback=broadcast_event
            )
            pipeline.process(
                input_file=str(input_path),
                output_dir=output_dir,
                model_key=model_key,
                output_format=req.format,
                overlap=overlap
            )
        except Exception as e:
            broadcast_event({"type": "error", "message": str(e)})

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()

    return {"status": "started", "output_dir": output_dir}

# Serve Frontend SPA
@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>Stem Separator Studio</h1>")
