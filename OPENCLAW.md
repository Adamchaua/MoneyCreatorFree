# OpenClaw Guide

MoneyCreatorFree expects:

- `PEXELS_API_KEY` in `.env`
- `MOSS_DIR` pointing to extracted MOSS-TTS-Nano
- FFmpeg and ffprobe available in PATH
- Whisper installed in the MOSS venv

Run examples with:

```bash
python -m moneycreator.cli batch --configs examples
```

Check each `outputs/<id>/qa.json` before declaring success.
