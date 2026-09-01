# Native OS Dialogs — 100% Thread-Safe & Tkinter-Free

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Optional

def pick_audio_file() -> Optional[str]:
    """
    Opens native OS file chooser dialog in an isolated process.
    Guarantees thread-safety and completely eliminates Tcl/Tk crashes.
    """
    os_name = platform.system()

    if os_name == "Windows":
        ps_script = """
Add-Type -AssemblyName System.Windows.Forms
$d = New-Object System.Windows.Forms.OpenFileDialog
$d.Title = "Seleccionar archivo de música"
$d.Filter = "Archivos de Audio (*.mp3;*.wav;*.flac;*.m4a;*.ogg;*.aac)|*.mp3;*.wav;*.flac;*.m4a;*.ogg;*.aac|Todos los Archivos (*.*)|*.*"
$d.RestoreDirectory = $true
$res = $d.ShowDialog()
if ($res -eq [System.Windows.Forms.DialogResult]::OK) {
    Write-Output $d.FileName
}
"""
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os_name == "Windows" else 0
            )
            out = res.stdout.strip()
            return out if out and Path(out).exists() else None
        except Exception:
            return None

    elif os_name == "Darwin":  # macOS
        osa_script = 'POSIX path of (choose file with prompt "Seleccionar archivo de audio" of type {"mp3", "wav", "flac", "m4a", "ogg", "aac"})'
        try:
            res = subprocess.run(["osascript", "-e", osa_script], capture_output=True, text=True)
            out = res.stdout.strip()
            return out if out and Path(out).exists() else None
        except Exception:
            return None

    else:  # Linux
        for cmd in [
            ["zenity", "--file-selection", "--title=Seleccionar archivo de audio", "--file-filter=Audio | *.mp3 *.wav *.flac *.m4a *.ogg *.aac"],
            ["kdialog", "--getopenfilename", ".", "*.mp3 *.wav *.flac *.m4a *.ogg *.aac"]
        ]:
            try:
                res = subprocess.run(cmd, capture_output=True, text=True)
                out = res.stdout.strip()
                if out and Path(out).exists():
                    return out
            except Exception:
                continue
        return None


def pick_folder() -> Optional[str]:
    """
    Opens native OS folder chooser dialog in an isolated process.
    """
    os_name = platform.system()

    if os_name == "Windows":
        ps_script = """
Add-Type -AssemblyName System.Windows.Forms
$d = New-Object System.Windows.Forms.FolderBrowserDialog
$d.Description = "Seleccionar carpeta de destino para los stems"
$d.ShowNewFolderButton = $true
$res = $d.ShowDialog()
if ($res -eq [System.Windows.Forms.DialogResult]::OK) {
    Write-Output $d.SelectedPath
}
"""
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os_name == "Windows" else 0
            )
            out = res.stdout.strip()
            return out if out and Path(out).exists() else None
        except Exception:
            return None

    elif os_name == "Darwin":  # macOS
        osa_script = 'POSIX path of (choose folder with prompt "Seleccionar carpeta de destino")'
        try:
            res = subprocess.run(["osascript", "-e", osa_script], capture_output=True, text=True)
            out = res.stdout.strip()
            return out if out and Path(out).exists() else None
        except Exception:
            return None

    else:  # Linux
        for cmd in [
            ["zenity", "--file-selection", "--directory", "--title=Seleccionar carpeta de destino"],
            ["kdialog", "--getexistingdirectory", "."]
        ]:
            try:
                res = subprocess.run(cmd, capture_output=True, text=True)
                out = res.stdout.strip()
                if out and Path(out).exists():
                    return out
            except Exception:
                continue
        return None
