import argparse
import json
from pathlib import Path

from .pipeline import create


def main():
    parser = argparse.ArgumentParser(description="MoneyCreatorFree short video generator")
    sub = parser.add_subparsers(dest="command", required=True)

    create_parser = sub.add_parser("create", help="Create a video from a YAML config")
    create_parser.add_argument("--config", required=True, help="Path to config YAML")
    create_parser.add_argument("--output-dir", default=None, help="Optional output root")

    batch_parser = sub.add_parser("batch", help="Create videos from all YAML configs in a directory")
    batch_parser.add_argument("--configs", default="examples", help="Directory containing YAML configs")
    batch_parser.add_argument("--output-dir", default=None, help="Optional output root")

    args = parser.parse_args()

    if args.command == "create":
        report = create(args.config, args.output_dir)
        print(json.dumps(report, indent=2))
        raise SystemExit(0 if report.get("passed") else 2)

    if args.command == "batch":
        reports = []
        for cfg in sorted(Path(args.configs).glob("*.yaml")):
            report = create(cfg, args.output_dir)
            reports.append(report)
            print(f"{'PASS' if report.get('passed') else 'FAIL'} {cfg.name} -> {report.get('final_video')}")
        failed = [r for r in reports if not r.get("passed")]
        print(json.dumps({"total": len(reports), "passed": len(reports)-len(failed), "failed": len(failed)}, indent=2))
        raise SystemExit(0 if not failed else 2)


if __name__ == "__main__":
    main()
