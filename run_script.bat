@echo off
where python >nul 2>nul
if errorlevel 1 (
	echo Python is not installed or not in PATH.
	pause
	exit /b 1
)
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%main_script.py"
if errorlevel 1 (
	echo The Python script failed.
	pause
)