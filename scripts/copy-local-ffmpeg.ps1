$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$vendor = Join-Path $root "vendor"
$ffmpegCommand = Get-Command ffmpeg -ErrorAction SilentlyContinue

if (-not $ffmpegCommand) {
    throw "ffmpeg was not found in PATH."
}

New-Item -ItemType Directory -Path $vendor -Force | Out-Null
Copy-Item -LiteralPath $ffmpegCommand.Source -Destination (Join-Path $vendor "ffmpeg.exe") -Force
Write-Host "Copied ffmpeg.exe to vendor\ffmpeg.exe"
