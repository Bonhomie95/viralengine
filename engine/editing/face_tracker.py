import cv2
from typing import Any
import mediapipe as mp

mp_face = mp.solutions.face_detection


def get_face_center(frame):
    with mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.5) as detector:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results: Any = detector.process(rgb)  # tell type checker to chill

        if getattr(results, "detections", None):
            box = results.detections[0].location_data.relative_bounding_box
            h, w, _ = frame.shape
            cx = int((box.xmin + box.width / 2) * w)
            cy = int((box.ymin + box.height / 2) * h)
            return cx, cy

    return None
