# Real-Time Progress Tracker & Stream Interceptor

import io
import re
import sys
import time
import logging
from typing import Callable, Optional, Dict, Any

PROGRESS_REGEX = re.compile(r'(\d+)/(\d+)\s*\[([^<]+)<([^,\]]+)')

class ProgressStreamWrapper(io.StringIO):
    """
    Wraps sys.stdout / sys.stderr to capture tqdm progress in real time.
    """
    def __init__(self, original_stream, event_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        super().__init__()
        self.original_stream = original_stream
        self.event_callback = event_callback
        self.buffer = ""

    def write(self, text: str):
        if not text:
            return 0

        # Also write to original stream if it exists and is writable
        if self.original_stream and hasattr(self.original_stream, "write"):
            try:
                self.original_stream.write(text)
                if hasattr(self.original_stream, "flush"):
                    self.original_stream.flush()
            except Exception:
                pass

        self.buffer += text
        if "\r" in self.buffer or "\n" in self.buffer:
            lines = self.buffer.replace("\r", "\n").split("\n")
            for line in lines[:-1]:
                line_str = line.strip()
                if line_str and self.event_callback:
                    # Check for tqdm chunk pattern
                    match = PROGRESS_REGEX.search(line_str)
                    if match:
                        chunk_cur, chunk_total, elapsed, eta = match.groups()
                        try:
                            cur = int(chunk_cur)
                            tot = int(chunk_total)
                            pct = round((cur / tot) * 100, 1)
                            self.event_callback({
                                "type": "progress",
                                "percent": pct,
                                "chunk": cur,
                                "total_chunks": tot,
                                "elapsed": elapsed.strip(),
                                "eta": eta.strip(),
                                "stage": f"Separando audio: Fragmento {cur} de {tot} ({pct}%) • Tiempo restante: {eta.strip()}"
                            })
                        except Exception:
                            pass
                    else:
                        if not any(k in line_str for k in ["%", "it/s", "s/it"]):
                            self.event_callback({
                                "type": "log",
                                "message": line_str
                            })
            self.buffer = lines[-1]

        return len(text)

    def flush(self):
        if self.original_stream and hasattr(self.original_stream, "flush"):
            try:
                self.original_stream.flush()
            except Exception:
                pass


class UnifiedLogHandler(logging.Handler):
    """
    Captures standard library logs and forwards them to the event callback.
    """
    def __init__(self, event_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        super().__init__()
        self.event_callback = event_callback
        self.setFormatter(logging.Formatter('%(message)s'))

    def emit(self, record):
        if not self.event_callback:
            return
        try:
            msg = self.format(record).strip()
            if not msg:
                return

            # Check if log message has progress info
            match = PROGRESS_REGEX.search(msg)
            if match:
                chunk_cur, chunk_total, elapsed, eta = match.groups()
                try:
                    cur = int(chunk_cur)
                    tot = int(chunk_total)
                    pct = round((cur / tot) * 100, 1)
                    self.event_callback({
                        "type": "progress",
                        "percent": pct,
                        "chunk": cur,
                        "total_chunks": tot,
                        "elapsed": elapsed.strip(),
                        "eta": eta.strip(),
                        "stage": f"Separando audio: Fragmento {cur} de {tot} ({pct}%) • Tiempo restante: {eta.strip()}"
                    })
                except Exception:
                    pass
            else:
                self.event_callback({
                    "type": "log",
                    "message": msg
                })
        except Exception:
            pass
