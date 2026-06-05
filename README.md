# 🎬 MoneyCreatorFree

Free, local-first short-video creation engine for agents and creators.

MoneyCreatorFree turns an idea or YAML config into a vertical short video using MOSS-TTS, Whisper subtitles, free Pexels stock video, FFmpeg rendering, and strict QA.

<img src="assets/infographic/pipeline.svg" alt="Pipeline" width="100%" />

## 🚀 Features

- MOSS-TTS local voice generation
- Adam voice by default, natural pitch
- Whisper auto-synced subtitles from the generated voice
- Pexels stock video matching by scene keywords
- Multiple stock clips per video, stitched to match narration length
- Minimal subtitle style using DejaVu Sans Condensed
- FFmpeg 9:16 renderer with lightweight motion overlays
- Strict QA report for every render
- Agent-ready docs for Hermes, OpenClaw, Claude Code, and Codex-style agents

## ⚡ Quickstart

```bash
git clone <your-repo-url> MoneyCreatorFree
cd MoneyCreatorFree
cp .env.example .env
```

Edit `.env`:

```text
PEXELS_API_KEY=your_pexels_key_here
MOSS_DIR=/path/to/MOSS-TTS-Nano-main
```

Run one example:

```bash
python -m moneycreator.cli create --config examples/economy_15s.yaml
```

Run all examples:

```bash
python -m moneycreator.cli batch --configs examples
```

## 💡 Example Topics & Demos

| File | Topic | Category | Target | Demo |
| --- | --- | --- | --- | --- |
| `examples/economy_15s.yaml` | Why prices keep rising | Economy | 15s | [🎥 Watch](assets/demos/economy.mp4) |
| `examples/society_15s.yaml` | Attention is social power | Society | 15s | [🎥 Watch](assets/demos/society.mp4) |
| `examples/finance_15s.yaml` | The first rule of personal finance | Finance | 15s | [🎥 Watch](assets/demos/finance.mp4) |

## 📂 Output Structure

```text
outputs/<run_id>/
├── config.yaml
├── script.txt
├── voice.wav
├── subtitle.ass
├── stock_manifest.json
├── final.mp4
└── qa.json
```

## ✅ QA Checks

Each run checks:

- target duration within tolerance
- audio/video sync under 0.3s
- subtitle has at least 3 segments
- transcript coverage at least 70%
- at least 3 stock clips
- final video file size above 300KB

## 🤖 Agent Compatibility

This repo includes:

- `AGENTS.md` for Hermes/Codex-style agents
- `CLAUDE.md` for Claude Code
- `OPENCLAW.md` for OpenClaw

Agents should read those files before editing or running the pipeline.

## 🔒 Important Security Note

Do not commit `.env` or real API keys. Users only need to add their own Pexels API key after cloning.

## ❤️ Donate

If MoneyCreatorFree helps your workflow, you can support the project.

- **PayPal:** `ckelvinkhanh32@gmail.com`
- **GitHub Sponsors:** [https://github.com/sponsors/Adamchaua](https://github.com/sponsors/Adamchaua)
- **EVM Wallet (ETH/BNB/Polygon etc):** `0x1ecab01075f3bdf1b56b7D849c8e28ef88943624`

## 🗺️ Roadmap

- Pixabay provider
- JSON/YAML batch templates
- word-by-word subtitles
- music bed with ducking
- stock quality scoring
- multi-variant render and auto-select best
