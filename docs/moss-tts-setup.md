# MOSS-TTS Setup

MoneyCreatorFree can install MOSS-TTS-Nano for you into the ignored `third_party/` folder. You can also point `MOSS_DIR` in `.env` to an existing MOSS-TTS-Nano checkout.

## Requirements

- Python 3.10+
- FFmpeg and FFprobe available in `PATH`
- Git
- A working MOSS-TTS-Nano checkout with `infer_onnx.py`
- Whisper installed in the same MOSS virtual environment

## 1. Install system tools

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y git ffmpeg python3 python3-venv python3-pip
```

Windows users can install FFmpeg from:

```text
https://ffmpeg.org/download.html
```

Then make sure `ffmpeg` and `ffprobe` work from the terminal.

## 2. Prepare MOSS-TTS

Recommended automated setup from inside MoneyCreatorFree:

```bash
python -m moneycreator.cli setup-moss
```

This clones `OpenMOSS/MOSS-TTS-Nano` into:

```text
third_party/MOSS-TTS-Nano
```

Then it creates a MOSS `.venv`, installs `requirements.txt`, and installs `openai-whisper`.

You can also use an existing MOSS-TTS-Nano checkout:

```bash
cd ~/work
git clone https://github.com/OpenMOSS/MOSS-TTS-Nano.git MOSS-TTS-Nano-main
cd MOSS-TTS-Nano-main
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install openai-whisper
```

If your MOSS-TTS distribution has its own install script, use that script, but keep the `.venv` folder inside the MOSS directory.

## 3. Verify MOSS-TTS manually

From the MOSS-TTS directory:

```bash
. .venv/bin/activate
printf "Hello, this is a MoneyCreatorFree voice test." > /tmp/moss_test.txt
python infer_onnx.py \
  --voice Adam \
  --text-file /tmp/moss_test.txt \
  --output-audio-path /tmp/moss_test.wav \
  --disable-wetext-processing \
  --cpu-threads 4 \
  --max-new-frames 500
```

Verify the audio file exists:

```bash
ffprobe /tmp/moss_test.wav
```

## 4. Connect MOSS-TTS to MoneyCreatorFree

In this repo:

```bash
cp .env.example .env
```

Edit `.env`:

```text
MOSS_DIR=/absolute/path/to/MOSS-TTS-Nano-main
PEXELS_API_KEY=your_pexels_api_key_here
```

Important: `MOSS_DIR` must be an absolute path and must contain both:

```text
infer_onnx.py
.venv/
```

## 5. Run a smoke test

```bash
python -m moneycreator.cli create --config examples/economy_15s.yaml
```

A successful run creates:

```text
outputs/economy_15s/final.mp4
outputs/economy_15s/qa.json
```

Open `qa.json` and confirm:

```json
{
  "passed": true
}
```

## Troubleshooting

- `MOSS_DIR is not set or does not exist`: set the absolute MOSS path in `.env`.
- `infer_onnx.py` not found: `MOSS_DIR` points to the wrong folder.
- `whisper: command not found`: activate the MOSS `.venv` and run `pip install openai-whisper`.
- `ffprobe` or `ffmpeg` not found: install FFmpeg and add it to `PATH`.
- No stock videos downloaded: check `PEXELS_API_KEY` and the search terms in the YAML config.
