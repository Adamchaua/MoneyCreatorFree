import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MOSS_REPO = "https://github.com/OpenMOSS/MOSS-TTS-Nano.git"
DEFAULT_MOSS_DIR = ROOT / "third_party" / "MOSS-TTS-Nano"


def run(cmd, cwd=None, timeout=1800):
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(map(str, cmd))}\n{proc.stdout[-4000:]}")
    return proc.stdout


def resolve_moss_dir(env=None):
    env = env or os.environ
    candidates = []
    if env.get("MOSS_DIR"):
        candidates.append(Path(env["MOSS_DIR"]).expanduser())
    candidates.append(DEFAULT_MOSS_DIR)
    for candidate in candidates:
        if is_moss_ready(candidate):
            return candidate
    return None


def is_moss_ready(path):
    path = Path(path).expanduser()
    return (path / "infer_onnx.py").exists() and (path / ".venv").exists()


def venv_python(path):
    path = Path(path)
    if os.name == "nt":
        return path / ".venv" / "Scripts" / "python.exe"
    return path / ".venv" / "bin" / "python"


def venv_bin(path, command):
    path = Path(path)
    if os.name == "nt":
        return path / ".venv" / "Scripts" / f"{command}.exe"
    return path / ".venv" / "bin" / command


def install_moss(target_dir=None, repo_url=DEFAULT_MOSS_REPO, force=False):
    target = Path(target_dir or DEFAULT_MOSS_DIR).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and force:
        raise RuntimeError(
            f"Refusing to delete existing MOSS directory: {target}. Remove it manually if you want a clean install."
        )

    if not target.exists():
        run(["git", "clone", repo_url, str(target)], timeout=1800)

    if not (target / "infer_onnx.py").exists():
        raise RuntimeError(f"MOSS clone does not contain infer_onnx.py: {target}")

    py = venv_python(target)
    if not py.exists():
        run([sys.executable, "-m", "venv", ".venv"], cwd=target, timeout=300)

    run([str(py), "-m", "pip", "install", "-U", "pip"], cwd=target, timeout=600)
    requirements = target / "requirements.txt"
    if requirements.exists():
        run([str(py), "-m", "pip", "install", "-r", str(requirements)], cwd=target, timeout=1800)
    run([str(py), "-m", "pip", "install", "openai-whisper"], cwd=target, timeout=1800)

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise RuntimeError("FFmpeg/FFprobe not found in PATH. Install FFmpeg before rendering videos.")

    return target


def doctor(env=None):
    env = env or os.environ
    moss_dir = resolve_moss_dir(env)
    checks = []
    checks.append(("ffmpeg", shutil.which("ffmpeg") is not None, shutil.which("ffmpeg") or "missing"))
    checks.append(("ffprobe", shutil.which("ffprobe") is not None, shutil.which("ffprobe") or "missing"))
    checks.append(("MOSS_DIR", moss_dir is not None, str(moss_dir) if moss_dir else "missing"))
    if moss_dir:
        checks.append(("infer_onnx.py", (moss_dir / "infer_onnx.py").exists(), str(moss_dir / "infer_onnx.py")))
        checks.append(("MOSS venv", venv_python(moss_dir).exists(), str(venv_python(moss_dir))))
        checks.append(("whisper", venv_bin(moss_dir, "whisper").exists(), str(venv_bin(moss_dir, "whisper"))))
    checks.append(("PEXELS_API_KEY", bool(env.get("PEXELS_API_KEY", "").strip()), "set" if env.get("PEXELS_API_KEY", "").strip() else "missing"))
    return {"passed": all(ok for _, ok, _ in checks), "checks": checks, "moss_dir": str(moss_dir) if moss_dir else None}
