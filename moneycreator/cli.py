import argparse
import json
from pathlib import Path

from .moss import DEFAULT_MOSS_DIR, doctor, install_moss
from .pipeline import create, load_env
from .wizard import build_config_interactive, save_config


def print_doctor_report(report):
    for name, ok, detail in report["checks"]:
        mark = "PASS" if ok else "FAIL"
        print(f"{mark:4} {name}: {detail}")
    print(json.dumps({"passed": report["passed"], "moss_dir": report.get("moss_dir")}, indent=2))


def main():
    parser = argparse.ArgumentParser(description="MoneyCreatorFree end-to-end short video generator")
    sub = parser.add_subparsers(dest="command", required=True)

    setup_parser = sub.add_parser("setup-moss", help="Clone and prepare MOSS-TTS-Nano inside third_party/")
    setup_parser.add_argument("--target-dir", default=str(DEFAULT_MOSS_DIR), help="Install directory for MOSS-TTS-Nano")
    setup_parser.add_argument("--repo-url", default=None, help="Override the MOSS-TTS-Nano Git repository URL")

    doctor_parser = sub.add_parser("doctor", help="Check FFmpeg, MOSS-TTS, Whisper, and Pexels configuration")
    doctor_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON only")

    init_parser = sub.add_parser("init", help="Interactive wizard: create a YAML config from a topic")
    init_parser.add_argument("--output", default=None, help="Where to save the generated YAML config")
    init_parser.add_argument("--render", action="store_true", help="Render immediately after creating the config")

    create_parser = sub.add_parser("create", help="Create a video from a YAML config")
    create_parser.add_argument("--config", required=True, help="Path to config YAML")
    create_parser.add_argument("--output-dir", default=None, help="Optional output root")

    batch_parser = sub.add_parser("batch", help="Create videos from all YAML configs in a directory")
    batch_parser.add_argument("--configs", default="examples", help="Directory containing YAML configs")
    batch_parser.add_argument("--output-dir", default=None, help="Optional output root")

    args = parser.parse_args()

    if args.command == "setup-moss":
        target = install_moss(target_dir=args.target_dir, repo_url=args.repo_url or "https://github.com/OpenMOSS/MOSS-TTS-Nano.git")
        print(f"MOSS-TTS-Nano is ready at: {target}")
        print("Add this to .env if you want to pin the path:")
        print(f"MOSS_DIR={target}")
        return

    if args.command == "doctor":
        report = doctor(load_env())
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_doctor_report(report)
        raise SystemExit(0 if report["passed"] else 2)

    if args.command == "init":
        config = build_config_interactive()
        path = save_config(config, args.output)
        print(f"\nConfig saved: {path}")
        if args.render:
            report = create(path)
            print(json.dumps(report, indent=2))
            raise SystemExit(0 if report.get("passed") else 2)
        print("Render it with:")
        print(f"python -m moneycreator.cli create --config {path}")
        return

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
