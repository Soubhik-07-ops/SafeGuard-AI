import cv2
from ultralytics import YOLO
import cvzone
import os


class PPEDetector:

    def __init__(self):

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(project_root, "cv_models", "best.pt")

        self.model = YOLO(model_path)

        print("PPE Classes:", self.model.names)


    def process_frame(self, frame):

        violation_detected = False

        results = self.model(frame)[0]

        for box in results.boxes:

            conf = float(box.conf[0])

            # Confidence filtering
            if conf < 0.6:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cls = int(box.cls[0])
            label = self.model.names[cls]

            # Default color
            color = (0,255,0)

            # SAFETY VEST
            if label == "safety_vest":

                label_text = f"Vest {conf:.2f}"

                color = (0,255,0)

            # NO SAFETY VEST → VIOLATION
            elif label == "no_safety_vest":

                label_text = f"No Vest {conf:.2f}"

                color = (0,0,255)

                violation_detected = True

            # Draw label
            cvzone.putTextRect(
                frame,
                label_text,
                (x1,y1),
                scale=1,
                thickness=1
            )

            # Draw box
            cv2.rectangle(
                frame,
                (x1,y1),
                (x2,y2),
                color,
                2
            )

        # Show global violation text
        if violation_detected:

            cv2.putText(
                frame,
                "PPE VIOLATION!",
                (50,50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,0,255),
                3
            )

        return frame, violation_detected
