# Agent Instructions

MoneyCreatorFree is an agent-friendly short-video generator.

## Rules

- Do not commit real API keys. Use `.env.example` only.
- Read `README.md` and `docs/workflow.md` before editing.
- Use `examples/*.yaml` for demo configs.
- Store generated outputs under `outputs/` only.
- Always run QA before reporting success.
- Do not delete stock cache or outputs unless explicitly requested.

## Default Workflow

```bash
cp .env.example .env
# Fill PEXELS_API_KEY and MOSS_DIR
python -m moneycreator.cli create --config examples/economy_15s.yaml
python -m moneycreator.cli batch --configs examples
```

## Success Criteria

A run is successful only if `qa.json` has `passed: true` and `final.mp4` exists.
