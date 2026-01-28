import subprocess
import librosa
import numpy as np
from pathlib import Path


def extract_audio(video_path: str | Path) -> Path:
    video_path = Path(video_path)
    audio_path = video_path.with_suffix(".wav")

    if audio_path.exists():
        return audio_path

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-ac", "2",
        str(audio_path),
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return audio_path


def get_audio_spikes(video_path: str | Path):
    print("🎧 Extracting audio...")
    audio_path = extract_audio(video_path)

    print("⚡ Detecting audio spikes...")
    y, sr = librosa.load(str(audio_path), sr=None)
    print(f"🎼 Audio loaded, {len(y)/sr:.1f}s duration")
    energy = librosa.feature.rms(y=y)[0]

    threshold = np.percentile(energy, 90)
    spikes = np.where(energy > threshold)[0]
    times = librosa.frames_to_time(spikes, sr=sr)

    return times
