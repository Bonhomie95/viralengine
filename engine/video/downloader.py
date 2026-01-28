import subprocess
from pathlib import Path

DOWNLOAD_DIR = Path("data/downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def download_video(url: str, video_id: str) -> Path:
    out_template = DOWNLOAD_DIR / f"{video_id}.%(ext)s"

    base_cmd = [
        "yt-dlp",
        "--no-warnings",
        "--ignore-errors",
        "--retries",
        "5",
        "--fragment-retries",
        "5",
        "--extractor-args",
        "youtube:player_client=android",
        "-o",
        str(out_template),
        url,
    ]

    # Try best quality first
    try:
        print(f"⬇️ Downloading video: {video_id}")
        subprocess.run(base_cmd + ["-f", "bv*+ba/best"], check=True)
    except subprocess.CalledProcessError:
        print("⚠️ Best format failed. Trying fallback...")
        print("🎞 Normalizing video format...")
        subprocess.run(base_cmd + ["-f", "mp4"], check=True)
        print("✅ Video ready for AI analysis")


    files = list(DOWNLOAD_DIR.glob(f"{video_id}.*"))
    if not files:
        raise FileNotFoundError("Download failed completely.")

    raw_video = files[0]
    fixed_video = DOWNLOAD_DIR / f"{video_id}_fixed.mp4"

    # Convert to stable format for OpenCV
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(raw_video),
            "-vf",
            "scale=1280:-2",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "aac",
            str(fixed_video),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("🎞 Video normalized, ready for AI analysis")
    return fixed_video
