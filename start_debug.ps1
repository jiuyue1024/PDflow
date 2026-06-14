# 印流PDflow 调试启动脚本 (PowerShell版)
# 带终端日志，日志同时保存到 run_log.txt

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pythonExe = Join-Path $scriptDir "pyside6_env\Scripts\python.exe"
$mainScript = Join-Path $scriptDir "run_main.py"
$logFile = Join-Path $scriptDir "run_log.txt"

if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: Python not found: $pythonExe" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (Test-Path $logFile) { Remove-Item $logFile -Force }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PDflow DEBUG MODE" -ForegroundColor Cyan
Write-Host "  Log: $logFile" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& $pythonExe -u $mainScript 2>&1 | Tee-Object -FilePath $logFile

Write-Host ""
Write-Host "Program exited. Press Enter to close." -ForegroundColor Yellow
Read-Host
