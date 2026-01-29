import cv2
import numpy as np
from pathlib import Path

def crop_to_shorts(input_path: Path, output_path: Path):
    cap = cv2.VideoCapture(str(input_path))

    fps = cap.get(cv2.CAP_PROP_FPS)
    W_out, H_out = 1080, 1920

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (W_out, H_out))

    print("📱 Converting to cinematic Shorts format...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]

        # --- BLURRED BACKGROUND ---
        bg = cv2.resize(frame, (W_out, H_out))
        bg = cv2.GaussianBlur(bg, (55, 55), 0)

        # --- FOREGROUND (FIT TO WIDTH) ---
        scale = W_out / w
        new_w = W_out
        new_h = int(h * scale)

        fg = cv2.resize(frame, (new_w, new_h))

        # --- CENTER FOREGROUND ---
        y_offset = (H_out - new_h) // 2

        # Clip if taller than screen
        if y_offset < 0:
            fg = fg[abs(y_offset):abs(y_offset)+H_out, :]
            y_offset = 0

        bg[y_offset:y_offset+fg.shape[0], 0:fg.shape[1]] = fg

        out.write(bg)

    cap.release()
    out.release()
