import cv2
from pathlib import Path


def resize_icon(img, max_w):
    h, w = img.shape[:2]
    scale = max_w / w
    return cv2.resize(img, (int(w*scale), int(h*scale)))


def overlay(frame, img, x, y):
    ih, iw = img.shape[:2]
    if y + ih > frame.shape[0] or x + iw > frame.shape[1]:
        return  # skip if out of bounds

    roi = frame[y:y+ih, x:x+iw]
    alpha = img[:, :, 3] / 255.0

    for c in range(3):
        roi[:, :, c] = roi[:, :, c] * (1 - alpha) + img[:, :, c] * alpha


def add_overlays(video_path: Path, output_path: Path):
    logo = cv2.imread("assets/logo.png", cv2.IMREAD_UNCHANGED)
    like = cv2.imread("assets/like.png", cv2.IMREAD_UNCHANGED)
    sub = cv2.imread("assets/subscribe.png", cv2.IMREAD_UNCHANGED)

    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (w, h))

    logo = resize_icon(logo, 200)
    like = resize_icon(like, 120)
    sub = resize_icon(sub, 160)

    print("🎨 Rendering overlays...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        overlay(frame, logo, 20, 20)
        overlay(frame, like, w - 150, h - 300)
        overlay(frame, sub, 20, h - 300)

        out.write(frame)

    cap.release()
    out.release()
