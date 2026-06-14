# 印流PDflow 启动脚本 (PowerShell版)
# 日常使用 - 无终端窗口

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pythonExe = Join-Path $scriptDir "pyside6_env\Scripts\pythonw.exe"
$mainScript = Join-Path $scriptDir "run_main.py"

if (-not (Test-Path $pythonExe)) {
    [Console]::Error.WriteLine("ERROR: Python not found: $pythonExe")
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path $mainScript)) {
    [Console]::Error.WriteLine("ERROR: Script not found: $mainScript")
    Read-Host "Press Enter to exit"
    exit 1
}

Start-Process -FilePath $pythonExe -ArgumentList "`"$mainScript`""
exit 0
