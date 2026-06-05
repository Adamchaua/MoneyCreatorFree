$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Error "Python 3.10+ is required. Install Python first: https://www.python.org/downloads/"
}

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue) -or -not (Get-Command ffprobe -ErrorAction SilentlyContinue)) {
  Write-Error "ffmpeg/ffprobe are missing. Install FFmpeg first: https://ffmpeg.org/download.html"
}

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .

if (-not (Test-Path .env)) {
  Copy-Item .env.example .env
  Write-Host "Created .env from .env.example"
}

python -m moneycreator.cli setup-moss
python -m moneycreator.cli doctor

Write-Host ""
Write-Host "Setup complete. Add PEXELS_API_KEY to .env if doctor reports it missing."
Write-Host "Then run:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python -m moneycreator.cli init --render"
