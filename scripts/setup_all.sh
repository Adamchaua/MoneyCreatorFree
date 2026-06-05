#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required. Please install Python 3.10+ first." >&2
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  echo "ffmpeg/ffprobe are missing. Install FFmpeg first:" >&2
  echo "  Ubuntu/Debian: sudo apt update && sudo apt install -y ffmpeg" >&2
  echo "  macOS: brew install ffmpeg" >&2
  exit 1
fi

python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

python -m moneycreator.cli setup-moss
python -m moneycreator.cli doctor || true

echo
echo "Setup complete. Add PEXELS_API_KEY to .env if doctor reports it missing."
echo "Then run:"
echo "  . .venv/bin/activate"
echo "  python -m moneycreator.cli init --render"
