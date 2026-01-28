import numpy as np
from pathlib import Path
from .audio_spike_detector import get_audio_spikes
from .scene_change_detector import get_scene_changes


def find_best_moment(video_path: str | Path, clip_len=45):
    video_path = str(video_path)

    print("🎧 Extracting audio & analyzing spikes...")
    audio_times = get_audio_spikes(video_path)
    
    print("🎬 Detecting scene changes...")
    scenes = get_scene_changes(video_path)

    print("🧠 Scoring scenes...")

    scores = []
    

    for start, end in scenes:
        duration = end - start
        if duration < clip_len:
            continue

        spike_count = np.sum((audio_times >= start) & (audio_times <= end))
        scores.append((spike_count, start))

    if not scores:
        return 0, clip_len

    best_start = max(scores)[1]
    return best_start, best_start + clip_len
