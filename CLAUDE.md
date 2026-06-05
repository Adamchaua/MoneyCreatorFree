# Claude Code Guide

Use this repo as a config-driven video pipeline. Keep API keys out of git.

Preferred commands:

```bash
python -m moneycreator.cli create --config examples/economy_15s.yaml
python -m moneycreator.cli batch --configs examples
```

When changing the pipeline, update `README.md`, `docs/workflow.md`, and at least one example config if behavior changes.
