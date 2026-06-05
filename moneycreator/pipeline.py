import json
import os
import re
import subprocess
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_env(root=ROOT):
    env = dict(os.environ)
    env_file = root / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env.setdefault(k.strip(), v.strip())
    return env


def run(cmd, cwd=None, timeout=300):
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


def slugify(text):
    return re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_") or "video"


def duration(path):
    out = run([
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=nk=1:nw=1",
        str(path),
    ], timeout=30)
    return float(out.strip())


def ass_time(t):
    h = int(t // 3600)
    t -= h * 3600
    m = int(t // 60)
    t -= m * 60
    return f"{h}:{m:02d}:{t:05.2f}"


def srt_time(t):
    h = int(t // 3600)
    t -= h * 3600
    m = int(t // 60)
    t -= m * 60
    s = int(t)
    ms = int(round((t - s) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def load_config(config_path):
    data = yaml.safe_load(Path(config_path).read_text())
    if not data:
        raise ValueError(f"Empty config: {config_path}")
    return data


def create_voice(config, run_dir, env):
    moss_dir = Path(env.get("MOSS_DIR") or "")
    if not moss_dir.exists():
        raise RuntimeError("MOSS_DIR is not set or does not exist. Copy .env.example to .env and set MOSS_DIR.")
    voice = config.get("voice", {}).get("name", "Adam")
    script_file = run_dir / "script.txt"
    raw = run_dir / "voice.wav"
    cmd = (
        f". .venv/bin/activate && python infer_onnx.py --voice {voice} "
        f"--text-file {script_file} --output-audio-path {raw} "
        "--disable-wetext-processing --cpu-threads 4 --max-new-frames 500"
    )
    run(["bash", "-lc", cmd], cwd=moss_dir, timeout=300)
    return raw


def transcribe(config, audio, run_dir, env):
    moss_dir = Path(env.get("MOSS_DIR") or "")
    asr_dir = run_dir / "asr"
    asr_dir.mkdir(exist_ok=True)
    model = config.get("subtitle", {}).get("whisper_model", "tiny")
    lang = config.get("language", "English")
    cmd = (
        f". .venv/bin/activate && whisper {audio} --model {model} "
        f"--language {lang} --task transcribe --output_format json "
        f"--output_dir {asr_dir} --fp16 False"
    )
    run(["bash", "-lc", cmd], cwd=moss_dir, timeout=240)
    return asr_dir / f"{Path(audio).stem}.json"


def make_ass(config, asr_json, ass_path):
    data = json.loads(Path(asr_json).read_text())
    font = config.get("subtitle", {}).get("font", "DejaVu Sans Condensed")
    main_size = int(config.get("subtitle", {}).get("font_size", 42))
    hook_size = main_size + 6
    header = f"""[Script Info]\nScriptType: v4.00+\nPlayResX: 720\nPlayResY: 1280\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Main,{font},{main_size},&H00FFFFFF,&H000000FF,&H00111111,&H99000000,-1,0,0,0,100,100,0,0,1,3,1,2,70,70,150,1\nStyle: Hook,{font},{hook_size},&H00FFFFFF,&H000000FF,&H00111111,&H99000000,-1,0,0,0,100,100,0,0,1,3,1,2,68,68,180,1\nStyle: Small,{font},24,&H00D8E8F2,&H000000FF,&H00111111,&H66000000,0,0,0,100,100,1,0,1,2,1,8,50,50,62,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"""
    lines = [header]
    segments = data.get("segments", [])
    for i, seg in enumerate(segments):
        text = " ".join(seg.get("text", "").strip().split())
        if not text:
            continue
        words = text.split()
        if len(words) > 8:
            mid = len(words) // 2
            text = " ".join(words[:mid]) + r"\N" + " ".join(words[mid:])
        style = "Hook" if i in (0, len(segments) - 1) else "Main"
        lines.append(f"Dialogue: 0,{ass_time(seg['start'])},{ass_time(seg['end'])},{style},,0,0,0,,{text}\n")
    if segments:
        end = max(s["end"] for s in segments)
        lines.append(f"Dialogue: 0,0:00:00.00,{ass_time(end)},Small,,0,0,0,,MONEYCREATORFREE\n")
    ass_path.write_text("".join(lines))
    return ass_path


def pexels_search_download(config, run_dir, env):
    api_key = env.get("PEXELS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY is not set. Copy .env.example to .env and add your own Pexels key.")
    headers = {"Authorization": api_key}
    stock_cache = Path(env.get("MONEYCREATOR_STOCK_CACHE") or ROOT / "stock_cache")
    stock_cache.mkdir(exist_ok=True)
    clips = []
    terms = config.get("stock", {}).get("terms", [])
    per_term = int(config.get("stock", {}).get("clips_per_term", 1))
    for term in terms:
        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params={"query": term, "orientation": "portrait", "per_page": 12},
            timeout=30,
        )
        if resp.status_code != 200:
            continue
        found = 0
        for item in resp.json().get("videos", []):
            best = None
            for file in item.get("video_files", []):
                w, h = int(file.get("width") or 0), int(file.get("height") or 0)
                link = file.get("link")
                if link and h >= w and h >= 960:
                    score = (h, w)
                    if best is None or score > best[0]:
                        best = (score, link)
            if not best:
                continue
            name = stock_cache / f"{slugify(term)}_{item.get('id')}.mp4"
            if not name.exists() or name.stat().st_size < 100_000:
                video = requests.get(best[1], timeout=90)
                if video.status_code == 200 and len(video.content) > 100_000:
                    name.write_bytes(video.content)
            if name.exists() and name.stat().st_size > 100_000:
                clips.append({"term": term, "path": str(name), "pexels_id": item.get("id")})
                found += 1
            if found >= per_term:
                break
    (run_dir / "stock_manifest.json").write_text(json.dumps(clips, indent=2))
    if not clips:
        raise RuntimeError("No stock videos downloaded. Check Pexels API key or search terms.")
    return [Path(c["path"]) for c in clips]


def render(config, clips, audio, ass, output):
    total = duration(audio)
    clip_d = total / max(len(clips), 1)
    inputs = []
    filters = []
    for i, clip in enumerate(clips):
        inputs += ["-stream_loop", "-1", "-i", str(clip)]
        filters.append(
            f"[{i}:v]trim=duration={clip_d:.3f},setpts=PTS-STARTPTS,"
            "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,"
            "eq=contrast=1.08:saturation=1.10:brightness=-0.035"
            f"[v{i}]"
        )
    inputs += ["-i", str(audio)]
    filters.append("".join(f"[v{i}]" for i in range(len(clips))) + f"concat=n={len(clips)}:v=1:a=0[base]")
    title = config.get("topic", "MoneyCreatorFree").upper().replace("'", "")[:34]
    font = config.get("render", {}).get("title_font", "DejaVuSansCondensed-Bold")
    vf = (
        "[base]drawbox=x=0:y=0:w=720:h=1280:color=0x000000@0.17:t=fill,"
        "drawbox=x='-160+mod(t*115,900)':y=95:w=230:h=230:color=0x00e7ff@0.13:t=fill,"
        "drawbox=x='720-mod(t*82,980)':y=805:w=290:h=290:color=0xff8a00@0.11:t=fill,"
        f"drawtext=text='{title}':font={font}:fontcolor=white:fontsize=34:x=48:y=102:alpha='0.80+0.20*sin(t*2)',"
        f"ass={ass},format=yuv420p[v]"
    )
    filters.append(vf)
    audio_index = len(clips)
    run([
        "ffmpeg", "-y", *inputs, "-t", f"{total:.3f}",
        "-filter_complex", ";".join(filters),
        "-map", "[v]", "-map", f"{audio_index}:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(output),
    ], timeout=240)
    return output


def qa(config, run_dir, audio, asr_json, video, clips):
    audio_d = duration(audio)
    video_d = duration(video)
    data = json.loads(Path(asr_json).read_text())
    transcript = " ".join(seg.get("text", "") for seg in data.get("segments", [])).lower()
    script = (run_dir / "script.txt").read_text().lower()
    words = re.findall(r"[a-zA-Z]+", script)
    coverage = sum(1 for w in words if w in transcript) / max(len(words), 1)
    target = float(config.get("duration_target", 15))
    tolerance = float(config.get("qa", {}).get("duration_tolerance", 4))
    checks = [
        ("duration_target", abs(audio_d - target) <= tolerance, audio_d),
        ("audio_video_sync", abs(audio_d - video_d) <= 0.3, abs(audio_d - video_d)),
        ("subtitle_segments", len(data.get("segments", [])) >= 3, len(data.get("segments", []))),
        ("transcript_coverage", coverage >= 0.70, coverage),
        ("stock_clip_count", len(clips) >= 3, len(clips)),
        ("video_file_size", Path(video).stat().st_size > 300_000, Path(video).stat().st_size),
    ]
    report = {
        "passed": all(ok for _, ok, _ in checks),
        "topic": config.get("topic"),
        "audio_duration": audio_d,
        "video_duration": video_d,
        "stock_clip_count": len(clips),
        "checks": checks,
        "final_video": str(video),
    }
    (run_dir / "qa.json").write_text(json.dumps(report, indent=2))
    return report


def create(config_path, output_root=None):
    config_path = Path(config_path)
    config = load_config(config_path)
    env = load_env()
    output_base = Path(output_root or env.get("MONEYCREATOR_OUTPUT_DIR") or ROOT / "outputs")
    run_id = config.get("id") or slugify(config.get("topic", config_path.stem))
    run_dir = output_base / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "config.yaml").write_text(config_path.read_text())
    (run_dir / "script.txt").write_text(config["script"].strip())
    audio = create_voice(config, run_dir, env)
    asr = transcribe(config, audio, run_dir, env)
    ass = make_ass(config, asr, run_dir / "subtitle.ass")
    clips = pexels_search_download(config, run_dir, env)
    video = render(config, clips, audio, ass, run_dir / "final.mp4")
    report = qa(config, run_dir, audio, asr, video, clips)
    return report
