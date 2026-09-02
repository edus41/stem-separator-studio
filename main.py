# Stem Separator Studio — Ultimate Launcher

import os
import sys
import time
import socket
import asyncio
import webbrowser
import threading
import uvicorn
from pathlib import Path

# UTF-8 and Stdout protection
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Windows asyncio Proactor socket exception patch (Silences WinError 10054 permanently)
if sys.platform == "win32":
    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport
        _orig_call_connection_lost = _ProactorBasePipeTransport._call_connection_lost

        def _silenced_call_connection_lost(self, exc):
            try:
                _orig_call_connection_lost(self, exc)
            except (ConnectionResetError, OSError):
                pass

        _ProactorBasePipeTransport._call_connection_lost = _silenced_call_connection_lost
    except Exception:
        pass

def find_free_port(start_port=7860):
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return 7860

def open_browser_delayed(url):
    time.sleep(1.2)
    webbrowser.open(url)

def main():
    port = find_free_port()
    url = f"http://127.0.0.1:{port}"

    print("=" * 60)
    print("  STEM SEPARATOR STUDIO v3.5 MASTER")
    print("  Full Multitrack 14-Stems | Mel-Band RoFormer | DrumSep | Demucs")
    print("=" * 60)
    print(f"Servidor web local activo en: {url}")
    print("Abriendo interfaz de estudio en tu navegador...")
    print("-" * 60)

    # Launch browser automatically
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()

    # Run Uvicorn server
    from web.server import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

if __name__ == "__main__":
    main()
