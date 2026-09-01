@echo off
title Stem Separator Studio
set VENV_PYTHON=C:\Users\infor\.gemini\antigravity\scratch\bs-roformer-runner\.venv\Scripts\python.exe
set APP_MAIN=C:\Users\infor\Desktop\Stem_Separator_Studio\main.py

if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" "%APP_MAIN%"
) else (
    python "%APP_MAIN%"
)
pause
