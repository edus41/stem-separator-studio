# Native OS Dialogs — 100% Thread-Safe & STA Topmost

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Optional

def pick_audio_file() -> Optional[str]:
    """
    Opens native OS file chooser dialog in an isolated STA sub-process.
    """
    os_name = platform.system()

    if os_name == "Windows":
        ps_script = """
[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null
$form = New-Object System.Windows.Forms.Form
$form.TopMost = $true
$form.Opacity = 0
$form.Show()
$d = New-Object System.Windows.Forms.OpenFileDialog
$d.Title = "Select Music File"
$d.Filter = "Audio Files (*.mp3;*.wav;*.flac;*.m4a;*.ogg;*.aac)|*.mp3;*.wav;*.flac;*.m4a;*.ogg;*.aac|All Files (*.*)|*.*"
$d.RestoreDirectory = $true
if ($d.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) {
    Write-Output $d.FileName
}
$form.Dispose()
"""
        try:
            res = subprocess.run(
                ["powershell", "-Sta", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os_name == "Windows" else 0,
                timeout=120
            )
            out = res.stdout.strip()
            return out if out and Path(out).exists() else None
        except Exception:
            return None

    elif os_name == "Darwin":  # macOS
        osa_script = 'POSIX path of (choose file with prompt "Select Audio File" of type {"mp3", "wav", "flac", "m4a", "ogg", "aac"})'
        try:
            res = subprocess.run(["osascript", "-e", osa_script], capture_output=True, text=True, timeout=120)
            out = res.stdout.strip()
            return out if out and Path(out).exists() else None
        except Exception:
            return None

    else:  # Linux
        for cmd in [
            ["zenity", "--file-selection", "--title=Select Audio File", "--file-filter=Audio | *.mp3 *.wav *.flac *.m4a *.ogg *.aac"],
            ["kdialog", "--getopenfilename", ".", "*.mp3 *.wav *.flac *.m4a *.ogg *.aac"]
        ]:
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                out = res.stdout.strip()
                if out and Path(out).exists():
                    return out
            except Exception:
                continue
        return None


def pick_folder() -> Optional[str]:
    """
    Opens native OS folder chooser dialog in an isolated STA sub-process.
    """
    os_name = platform.system()

    if os_name == "Windows":
        ps_script = """
[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null
$form = New-Object System.Windows.Forms.Form
$form.TopMost = $true
$form.Opacity = 0
$form.Show()
$d = New-Object System.Windows.Forms.FolderBrowserDialog
$d.Description = "Select Destination Folder for Stems"
$d.ShowNewFolderButton = $true
if ($d.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) {
    Write-Output $d.SelectedPath
}
$form.Dispose()
"""
        try:
            res = subprocess.run(
                ["powershell", "-Sta", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os_name == "Windows" else 0,
                timeout=120
            )
            out = res.stdout.strip()
            return out if out and Path(out).exists() else None
        except Exception:
            return None

    elif os_name == "Darwin":  # macOS
        osa_script = 'POSIX path of (choose folder with prompt "Select Destination Folder")'
        try:
            res = subprocess.run(["osascript", "-e", osa_script], capture_output=True, text=True, timeout=120)
            out = res.stdout.strip()
            return out if out and Path(out).exists() else None
        except Exception:
            return None

    else:  # Linux
        for cmd in [
            ["zenity", "--file-selection", "--directory", "--title=Select Destination Folder"],
            ["kdialog", "--getexistingdirectory", "."]
        ]:
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                out = res.stdout.strip()
                if out and Path(out).exists():
                    return out
            except Exception:
                continue
        return None
