$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent $scriptDir
$pythonExe = Join-Path $projectRoot "venv\Scripts\python.exe"
$spec = Join-Path $projectRoot "PDflow_vNext_Beta.spec"
$distPath = Join-Path $projectRoot "build\h4b-dist"
$workPath = Join-Path $projectRoot "build\h4b-work"

if (-not (Test-Path $pythonExe)) {
    throw "Clean venv not found: $pythonExe"
}
if (-not (Test-Path $spec)) {
    throw "Packaging spec not found: $spec"
}

Push-Location $projectRoot
try {
    & $pythonExe -m PyInstaller --noconfirm --clean `
        --distpath $distPath --workpath $workPath $spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
