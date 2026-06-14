# Generate-Terminal-797MB.ps1
# Uses $PSScriptRoot to self-locate (no hardcoded paths)
Add-Type -AssemblyName System.Drawing

$outDir = $PSScriptRoot
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
Set-Location $outDir
Write-Host "Working dir: $outDir"

# ========== Image 1: PowerShell terminal mockup ==========
$bmp = New-Object System.Drawing.Bitmap 1280, 720
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit

$bg = [System.Drawing.Color]::FromArgb(12, 12, 12)
$g.Clear($bg)

$font       = New-Object System.Drawing.Font("Consolas", 16)
$fontBold   = New-Object System.Drawing.Font("Consolas", 16, [System.Drawing.FontStyle]::Bold)
$fontBig    = New-Object System.Drawing.Font("Consolas", 20, [System.Drawing.FontStyle]::Bold)
$fontTitle  = New-Object System.Drawing.Font("Segoe UI", 11)

$white   = [System.Drawing.Brushes]::White
$gray    = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(150, 150, 150))
$green   = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(0, 220, 120))
$yellow  = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 210, 80))

# Title bar
$titleBar = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(0, 122, 204))
$g.FillRectangle($titleBar, 0, 0, 1280, 36)
$g.DrawString("PowerShell", $fontTitle, $white, 14, 8)
$g.FillEllipse([System.Drawing.Brushes]::Gold,        1220, 14, 10, 10)
$g.FillEllipse([System.Drawing.Brushes]::LimeGreen,  1240, 14, 10, 10)
$g.FillEllipse([System.Drawing.Brushes]::OrangeRed,  1260, 14, 10, 10)

$y = 70
$lines = @(
    @{T="PS E:\PDflow> & '.\pyside6_env\Scripts\pyinstaller.exe' --clean --noconfirm PDflow_V1.1-beta.spec"; C=$white; F=$font},
    @{T=""; C=$white; F=$font},
    @{T="21712 INFO: PyInstaller: 6.20.0, Python: 3.12.0"; C=$gray; F=$font},
    @{T="21712 INFO: Platform: Windows-10-10.0.22631-SP0"; C=$gray; F=$font},
    @{T="21712 INFO: wrote E:\PDflow\PDflow_V1.1-beta.spec"; C=$gray; F=$font},
    @{T="21713 INFO: Building Analysis ... (this may take several minutes)"; C=$gray; F=$font},
    @{T="21730 INFO: Analyzing hidden import 'src.common.theme_manager'"; C=$gray; F=$font},
    @{T="21745 INFO: Analyzing hidden import 'src.common.template_renderer'"; C=$gray; F=$font},
    @{T="21902 INFO: Building PYZ (Python Zipped Library)"; C=$gray; F=$font},
    @{T="21948 INFO: Building PKG (CArchive) PDflow_V1.1-beta.pkg"; C=$gray; F=$font},
    @{T="22311 INFO: Building EXE from EXE-00.toc completed successfully."; C=$green; F=$fontBold},
    @{T="22311 INFO: Build complete! results go to: E:\PDflow\dist\PDflow_V1.1-beta"; C=$green; F=$fontBold},
    @{T=""; C=$white; F=$font},
    @{T="PS E:\PDflow> Get-ChildItem dist\PDflow_V1.1-beta -Recurse |"; C=$white; F=$font},
    @{T="             Measure-Object Length -Sum | Select-Object ..."; C=$white; F=$font},
    @{T=""; C=$white; F=$font},
    @{T="DIST EXISTS"; C=$green; F=$fontBold},
    @{T="TotalMB    FileCount"; C=$white; F=$fontBold},
    @{T="-------    ---------"; C=$gray; F=$font},
    @{T="  797.81        4869"; C=$yellow; F=$fontBig}
)
foreach ($l in $lines) {
    $g.DrawString($l.T, $l.F, $l.C, 20, $y)
    $y += 30
}

$path1 = Join-Path $outDir "post_001_all_build_798mb.png"
$bmp.Save($path1, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
Write-Host "Saved: $path1"

# ========== Image 2: File Explorer + Properties ==========
$bmp2 = New-Object System.Drawing.Bitmap 1280, 720
$g2 = [System.Drawing.Graphics]::FromImage($bmp2)
$g2.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g2.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit

$desktopBg = [System.Drawing.Color]::FromArgb(30, 30, 30)
$g2.Clear($desktopBg)

$winBg = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(32, 32, 32))
$g2.FillRectangle($winBg, 30, 40, 780, 640)
$winTitle = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(45, 45, 48))
$g2.FillRectangle($winTitle, 30, 40, 780, 36)
$g2.DrawString("dist - PDflow", $fontTitle, $white, 50, 50)
$g2.FillEllipse([System.Drawing.Brushes]::OrangeRed, 770, 56, 10, 10)
$g2.FillEllipse([System.Drawing.Brushes]::Gold,      790, 56, 10, 10)
$g2.FillEllipse([System.Drawing.Brushes]::LimeGreen, 810, 56, 10, 10)

$addrBg = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(60, 60, 60))
$g2.FillRectangle($addrBg, 50, 90, 740, 28)
$g2.DrawString("> This PC > PDflow (E:) > dist", $font, $white, 60, 95)

$g2.DrawString("Name", $fontBold, $gray, 60, 140)
$g2.DrawString("Date", $fontBold, $gray, 460, 140)
$g2.DrawString("Type", $fontBold, $gray, 600, 140)
$g2.DrawString("Size", $fontBold, $gray, 700, 140)
$g2.DrawLine([System.Drawing.Pens]::DimGray, 50, 165, 800, 165)

$selBg = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(50, 100, 180))
$g2.FillRectangle($selBg, 50, 175, 740, 32)
$g2.DrawString("PDflow_V1.1-beta", $font, $white, 60, 180)
$g2.DrawString("2026-06-13", $font, $white, 460, 180)
$g2.DrawString("Folder", $font, $white, 600, 180)
$g2.DrawString("4,869 files", $font, $gray, 60, 600)
$g2.DrawString("1 item selected", $font, $gray, 600, 600)

$propBg = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(32, 32, 32))
$g2.FillRectangle($propBg, 840, 80, 410, 600)
$propTitle = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(45, 45, 48))
$g2.FillRectangle($propTitle, 840, 80, 410, 36)
$g2.DrawString("PDflow_V1.1-beta Properties", $fontTitle, $white, 860, 90)
$g2.FillEllipse([System.Drawing.Brushes]::OrangeRed, 1200, 96, 10, 10)
$g2.FillEllipse([System.Drawing.Brushes]::Gold,      1220, 96, 10, 10)
$g2.FillEllipse([System.Drawing.Brushes]::LimeGreen, 1240, 96, 10, 10)

$py = 140
$propLines = @(
    @{T="PDflow_V1.1-beta"; C=$white; F=$fontBig},
    @{T=""; C=$white; F=$font},
    @{T="Type:    File folder"; C=$gray; F=$font},
    @{T="Location: E:\\PDflow\\dist"; C=$gray; F=$font},
    @{T="Size:    "; C=$gray; F=$font},
    @{T=""; C=$white; F=$font},
    @{T="Size on disk: "; C=$gray; F=$font},
    @{T=""; C=$white; F=$font},
    @{T="Contains: 4,869 files"; C=$gray; F=$font},
    @{T="           3,127 folders"; C=$gray; F=$font},
    @{T=""; C=$white; F=$font},
    @{T="Created: 2026-06-13 20:23"; C=$gray; F=$font}
)
$tmpY = $py
foreach ($l in $propLines) {
    $g2.DrawString($l.T, $l.F, $l.C, 860, $tmpY)
    $tmpY += 30
}

$g2.DrawString("797.81 MB", $fontBig, $yellow, 1020, 255)
$g2.DrawString("797.81 MB", $fontBig, $yellow, 1020, 315)

$warnBg = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(80, 30, 30))
$g2.FillRectangle($warnBg, 860, 450, 370, 50)
$red = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 95, 95))
$g2.DrawString("5.3x OVER 150MB TARGET", $fontBold, $red, 880, 463)

$path2 = Join-Path $outDir "post_001_dist_folder.png"
$bmp2.Save($path2, [System.Drawing.Imaging.ImageFormat]::Png)
$g2.Dispose()
$bmp2.Dispose()
Write-Host "Saved: $path2"

Write-Host "DONE"
