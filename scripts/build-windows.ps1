$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$ffmpeg = Join-Path $root "vendor\ffmpeg.exe"

if (-not (Test-Path -LiteralPath $ffmpeg)) {
    throw "Missing vendor\ffmpeg.exe. Add ffmpeg.exe before building."
}

Push-Location $root
try {
    python -m PyInstaller `
        --noconfirm `
        --clean `
        --windowed `
        --onefile `
        --name "TSVideoConverterGUI" `
        --add-binary "vendor\ffmpeg.exe;." `
        app.py
}
finally {
    Pop-Location
}
