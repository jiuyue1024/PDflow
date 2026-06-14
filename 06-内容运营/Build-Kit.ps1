# Build-Kit.ps1 (uses .NET API for safe Chinese paths)
$root = [System.IO.Path]::Combine("E:\印流PDflow项目", "印流PDflow_首帖素材包_post001_2026-06-13")
$subs = @("01_文案","02_配图","03_运营记录","04_备用工具","05_post002_素材")

if ([System.IO.Directory]::Exists($root)) {
    [System.IO.Directory]::Delete($root, $true)
}
[System.IO.Directory]::CreateDirectory($root) | Out-Null
foreach ($s in $subs) {
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::Combine($root, $s)) | Out-Null
}
Write-Host "ROOT: $root"
Get-ChildItem $root | ForEach-Object { Write-Host ("  " + $_.Name) }
