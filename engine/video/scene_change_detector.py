import cv2
from pathlib import Path


def get_scene_changes(video_path: str | Path, threshold=30):
    print("🎬 Starting scene detection...")

    cap = cv2.VideoCapture(str(video_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    scenes = []
    prev_gray = None
    frame_num = 0
    last_cut_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_num += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            score = diff.mean()

            if score > threshold:
                t = frame_num / fps
                scenes.append((last_cut_time, t))
                last_cut_time = t

        prev_gray = gray

        # Progress display
        if frame_num % 300 == 0:
            pct = (frame_num / total_frames) * 100
            print(f"📊 Scene scan progress: {pct:.1f}%")

    cap.release()

    if not scenes:
        print("⚠️ No cuts detected. Using full video.")
        return [(0, total_frames / fps)]

    print(f"🎞 Scenes detected: {len(scenes)}")
    return scenes
