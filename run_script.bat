@echo off
set SCRIPT_DIR=%~dp0
set VENV_PYTHON=%SCRIPT_DIR%venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo Virtual environment not found. Run setup first:
    echo   py -m venv venv
    echo   venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

"%VENV_PYTHON%" "%SCRIPT_DIR%main_script.py"
if errorlevel 1 (
    echo The Python script failed.
    pause
)
