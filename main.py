# Stem Separator Studio — Modern Web / Desktop Launcher

import os
import sys
import time
import socket
import webbrowser
import threading
import uvicorn
from pathlib import Path

# Redirect stdout/stderr if None (pythonw mode)
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
    print("  🎧 STEM SEPARATOR STUDIO v2.0")
    print("  Mel-Band RoFormer • BS-RoFormer • Demucs v4")
    print("=" * 60)
    print(f"Iniciando servidor web en: {url}")
    print("Abriendo interfaz moderna en tu navegador...")
    print("-" * 60)

    # Launch browser automatically
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()

    # Run Uvicorn server
    from web.server import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

if __name__ == "__main__":
    main()
