import cv2
from pathlib import Path

def crop_to_shorts(input_video: Path, output_video: Path):
    cap = cv2.VideoCapture(str(input_video))
    fps = cap.get(cv2.CAP_PROP_FPS)

    target_w, target_h = 1080, 1920

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_video), fourcc, fps, (target_w, target_h))

    print("📱 Converting to cinematic Shorts format...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Background (blurred)
        bg = cv2.resize(frame, (target_w, target_h))
        bg = cv2.GaussianBlur(bg, (55, 55), 0)

        # Foreground (fit height)
        h, w = frame.shape[:2]
        scale = target_h / h
        fg_w = int(w * scale)
        fg = cv2.resize(frame, (fg_w, target_h))

        x_offset = (target_w - fg_w) // 2
        bg[:, x_offset:x_offset+fg_w] = fg

        out.write(bg)

    cap.release()
    out.release()
