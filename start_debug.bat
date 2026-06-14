@echo off
chcp 65001 >nul

set "PROJECT_DIR=%~dp0"
set "PYTHON_EXE=%PROJECT_DIR%pyside6_env\Scripts\python.exe"
set "SCRIPT=%PROJECT_DIR%run_main.py"
set "LOG_FILE=%PROJECT_DIR%run_log.txt"

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found: %PYTHON_EXE%
    pause
    exit /b 1
)

echo ========================================
echo   PDflow DEBUG MODE
echo   - 控制台日志会同步输出到 run_log.txt
echo   - 关闭窗口或按 Ctrl+C 退出
echo ========================================
echo.

if exist "%LOG_FILE%" del "%LOG_FILE%"

"%PYTHON_EXE%" -u "%SCRIPT%" 2>&1 | tee "%LOG_FILE%"

if errorlevel 1 (
    echo.
    echo [ERROR] 程序异常退出，错误码: %errorlevel%
    echo 日志已保存到: %LOG_FILE%
    pause
) else (
    echo.
    echo 程序正常退出
    pause
)
