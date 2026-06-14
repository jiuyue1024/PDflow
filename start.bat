@echo off
set "PROJECT_DIR=%~dp0"
set "PYTHON_EXE=%PROJECT_DIR%pyside6_env\Scripts\pythonw.exe"
set "SCRIPT=%PROJECT_DIR%run_main.py"

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found: %PYTHON_EXE%
    pause
    exit /b 1
)

start "" "%PYTHON_EXE%" "%SCRIPT%"
exit /b 0
