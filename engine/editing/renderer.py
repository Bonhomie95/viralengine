from pathlib import Path
import subprocess
from .shorts_cropper import crop_to_shorts
from .overlays import add_overlays

def merge_audio(original_video: Path, silent_video: Path, final_video: Path):
    print("🔊 Merging original audio...")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent_video),
            "-i",
            str(original_video),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(final_video),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def render_shorts(clip_path: Path):
    shorts_path = clip_path.with_name(clip_path.stem + "_shorts.mp4")
    overlay_path = clip_path.with_name(clip_path.stem + "_overlay.mp4")
    final_path = clip_path.with_name(clip_path.stem + "_final.mp4")

    print("📱 Creating cinematic shorts layout...")
    crop_to_shorts(clip_path, shorts_path)

    print("🎨 Adding overlays...")
    add_overlays(shorts_path, overlay_path)

    merge_audio(clip_path, overlay_path, final_path)

    # Cleanup
    print("🧹 Cleaning up temporary files...")
    for f in [clip_path, shorts_path, overlay_path]:
        if f.exists():
            f.unlink()

    print("✅ Final video rendered:", final_path)
    return final_path
