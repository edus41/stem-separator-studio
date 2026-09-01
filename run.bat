@echo off
title Stem Separator Studio
set VENV_PYTHON=C:\Users\infor\.gemini\antigravity\scratch\bs-roformer-runner\.venv\Scripts\python.exe

if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" "%~dp0main.py"
) else (
    python "%~dp0main.py"
)
pause
