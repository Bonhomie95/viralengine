import subprocess
from pathlib import Path


CLIP_DIR = Path("data/clips")
CLIP_DIR.mkdir(parents=True, exist_ok=True)


def extract_clip(video_path, start, end, video_id):
    out = CLIP_DIR / f"{video_id}_clip.mp4"

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", str(video_path),
        "-c", "copy",
        str(out)
    ]
    
    print(f"✂️ Cutting clip from {start:.1f}s to {end:.1f}s")
    subprocess.run(cmd, check=True)
    return out
