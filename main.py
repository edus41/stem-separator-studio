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
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Windows asyncio Proactor socket exception filter
def silence_winerror_10054(loop, context):
    exception = context.get("exception")
    if isinstance(exception, ConnectionResetError) or (isinstance(exception, OSError) and getattr(exception, "winerror", None) == 10054):
        return  # Harmless Windows socket reset when browser closes or refreshes
    if loop.default_exception_handler:
        loop.default_exception_handler(context)

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
    if sys.platform == "win32":
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.set_exception_handler(silence_winerror_10054)
        except Exception:
            pass

    port = find_free_port()
    url = f"http://127.0.0.1:{port}"

    print("=" * 60)
    print("  🎧 STEM SEPARATOR STUDIO v2.5 ULTIMATE")
    print("  Mel-Band RoFormer • DrumSep 6S • Karaoke • DeReverb • Demucs v4")
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
