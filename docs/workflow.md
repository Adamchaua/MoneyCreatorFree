# Workflow

This document explains how a user or AI agent should interact with MoneyCreatorFree from idea to final video.

## Pipeline Overview

```text
Idea / YAML config
-> script.txt
-> MOSS-TTS voice.wav
-> Whisper transcript JSON
-> subtitle.ass
-> Pexels stock clips
-> FFmpeg render
-> QA report
-> final.mp4
```

## User Interaction Flow

MoneyCreatorFree supports two flows:

1. **Interactive wizard:** answer guided questions and let the CLI create the YAML config.
2. **Manual config:** edit a YAML file directly, run the CLI, then review `final.mp4` and `qa.json`.

### Interactive Wizard

```bash
python -m moneycreator.cli init
```

The wizard asks for:

- video topic
- category
- video length in minutes
- language
- MOSS voice
- subtitle font
- subtitle size
- Whisper model
- stock-video search terms
- custom script or suggested script

Render immediately after the wizard:

```bash
python -m moneycreator.cli init --render
```

### 1. Pick a Topic

Choose a short-video topic with a clear audience and message.

Good examples:

```text
Why prices keep rising
The first rule of personal finance
Attention is social power
```

### 2. Create or Edit a YAML Config

Start from one of the examples:

```bash
cp examples/economy_15s.yaml examples/my_video.yaml
```

Edit the key fields:

```yaml
topic: "Why prices keep rising"
language: English
target_duration: 15
script: |
  Prices do not rise by accident.
  They rise when money, supply, and demand stop moving together.
  Understand that, and inflation becomes easier to see.
voice:
  provider: moss
  name: Adam
subtitle:
  whisper_model: tiny
stock:
  terms:
    - economy money
    - grocery prices
    - people buying food
  clips_per_term: 1
```

### 3. Run One Video

```bash
python -m moneycreator.cli create --config examples/my_video.yaml
```

The CLI prints a JSON QA report and exits with:

- `0` when QA passes
- `2` when QA fails

### 4. Review the Output

Check:

```text
outputs/my_video/final.mp4
outputs/my_video/qa.json
outputs/my_video/script.txt
outputs/my_video/subtitle.ass
outputs/my_video/stock_manifest.json
```

A valid result must have:

```json
{
  "passed": true
}
```

### 5. Iterate

If the output is weak, change one thing at a time:

- Rewrite the hook in `script`.
- Add better Pexels search terms under `stock.terms`.
- Reduce or increase `target_duration`.
- Try a different MOSS voice if your MOSS install supports it.
- Increase `subtitle.whisper_model` from `tiny` to `base` for better transcription.

### 6. Run a Batch

```bash
python -m moneycreator.cli batch --configs examples
```

This renders every `*.yaml` file in the config directory.

## Agent Workflow

When an AI agent edits or runs this repo, follow this order:

1. Read `README.md`, `docs/moss-tts-setup.md`, and this file.
2. Never commit real API keys or `.env`.
3. Create or modify `examples/*.yaml` for new demos.
4. Run the CLI command for the target config.
5. Confirm `qa.json` has `passed: true`.
6. Only report success when `final.mp4` exists and QA passes.

## Current Limitations

- There is no web UI yet; interaction is CLI-based.
- MOSS-TTS is cloned into `third_party/` by `setup-moss`, but the large MOSS dependency is not committed to Git.
- Pexels is the only stock-video provider currently implemented.
- The wizard suggests scripts and stock keywords, but it does not yet call an LLM to generate advanced scripts.

## Useful Commands

```bash
python -m moneycreator.cli setup-moss
python -m moneycreator.cli doctor
python -m moneycreator.cli init
python -m moneycreator.cli init --render
python -m moneycreator.cli create --config examples/economy_15s.yaml
python -m moneycreator.cli batch --configs examples
```
