import cv2
from ultralytics import YOLO
import cvzone
import os


class FallDetector:

    def __init__(self):

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(project_root, "cv_models", "yolov8n.pt")

        self.model = YOLO(model_path)


    def process_frame(self, frame):

        fall_detected = False

        results = self.model(frame)[0]

        for box in results.boxes:

            cls = int(box.cls[0])

            if cls != 0:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            h = y2 - y1
            w = x2 - x1

            aspect_ratio = w / h

            if aspect_ratio > 1.2:

                label = "FALL"
                color = (0,0,255)

                fall_detected = True

            else:

                label = "Person"
                color = (0,255,0)

            cvzone.putTextRect(
                frame,
                label,
                (x1,y1),
                scale=1,
                thickness=1
            )

            cv2.rectangle(
                frame,
                (x1,y1),
                (x2,y2),
                color,
                2
            )

        return frame, fall_detected
