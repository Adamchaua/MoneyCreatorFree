# Hermes Agent Guide

MoneyCreatorFree is designed to be operated by Hermes and other coding agents.

## Golden Rules

- Never commit `.env`, API keys, generated MOSS files, `third_party/`, `outputs/`, or `stock_cache/`.
- Read `README.md`, `docs/workflow.md`, and `docs/moss-tts-setup.md` before editing.
- Use `python -m moneycreator.cli doctor` before rendering.
- Use example configs under `examples/` as the safest starting point.
- Report success only when `qa.json` has `passed: true` and `final.mp4` exists.

## Recommended Hermes Workflow

```bash
python -m moneycreator.cli doctor
python -m moneycreator.cli init
python -m moneycreator.cli create --config examples/economy_15s.yaml
```

For a fresh machine:

```bash
bash scripts/setup_all.sh
```

## Rendering Checklist

1. Confirm `PEXELS_API_KEY` exists in `.env`.
2. Confirm MOSS is ready with `python -m moneycreator.cli doctor`.
3. Create or edit a YAML config.
4. Render with `python -m moneycreator.cli create --config <config.yaml>`.
5. Open `outputs/<run_id>/qa.json`.
6. If QA fails, improve script length, stock terms, or subtitle settings before reporting success.

## Useful Files

- `moneycreator/cli.py`: CLI entrypoint.
- `moneycreator/pipeline.py`: render pipeline.
- `moneycreator/moss.py`: MOSS setup and environment checks.
- `moneycreator/wizard.py`: interactive config wizard.
- `examples/*.yaml`: demo configs.
- `docs/workflow.md`: user and agent workflow.
