import cv2
import numpy as np
import os
from ultralytics import YOLO
from shapely.geometry import Point, Polygon

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODEL_PATH = os.path.join(PROJECT_ROOT, "cv_models", "yolov8m.pt")


class IntrusionDetector:

    def __init__(self, model_path=DEFAULT_MODEL_PATH):

        self.model = YOLO(model_path)

        # Default polygon
        self.polygon_points = [

            (400,300),
            (900,300),
            (900,700),
            (400,700)

        ]

        self.polygon = Polygon(self.polygon_points)

        self.min_confidence = 0.5


    def process_frame(self, frame):

        intrusion_detected = False

        # Draw polygon
        cv2.polylines(
            frame,
            [np.array(self.polygon_points)],
            True,
            (0,0,255),
            2
        )

        results = self.model(
            frame,
            verbose=False,
            classes=[0]
        )[0]

        for box in results.boxes:

            conf = float(box.conf)

            if conf < self.min_confidence:
                continue

            x1,y1,x2,y2 = map(int, box.xyxy[0])

            feet_x = (x1+x2)//2
            feet_y = y2

            point = Point(feet_x, feet_y)
            bbox_poly = Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])

            if self.polygon.contains(point) or self.polygon.intersects(bbox_poly):

                intrusion_detected = True

                color = (0,0,255)
                label = "INTRUSION"

            else:

                color = (0,255,0)
                label = "Person"

            cv2.rectangle(
                frame,
                (x1,y1),
                (x2,y2),
                color,
                2
            )

            cv2.putText(
                frame,
                label,
                (x1,y1-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

        return frame, intrusion_detected
