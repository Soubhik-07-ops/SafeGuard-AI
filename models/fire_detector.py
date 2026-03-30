import cv2
import os
import numpy as np
from ultralytics import YOLO


class FireDetector:

    def __init__(self):

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_pt = os.path.join(project_root, "cv_models", "yolo12n.pt")
        model_onnx = os.path.join(project_root, "cv_models", "fire_best.onnx")

        self.input_size = 640
        self.conf_threshold = 0.5

        if os.path.exists(model_pt):
            self.mode = "yolo"
            self.model = YOLO(model_pt)
            self.names = self.model.names
            print("Fire model loaded from YOLOv12n .pt!")
        elif os.path.exists(model_onnx):
            self.mode = "onnx"
            self.net = cv2.dnn.readNetFromONNX(model_onnx)
            self.names = {0: "fire", 1: "smoke"}
            print("Fire model loaded from ONNX!")
        else:
            raise FileNotFoundError("No fire model found. Expected cv_models/yolo12n.pt or cv_models/fire_best.onnx")


    def process_frame(self, frame):

        fire_detected = False
        h, w = frame.shape[:2]

        if self.mode == "yolo":
            results = self.model(frame, verbose=False)[0]
            for box in results.boxes:
                conf = float(box.conf[0]) if hasattr(box.conf, "__len__") else float(box.conf)
                if conf < self.conf_threshold:
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0]) if hasattr(box.cls, "__len__") else int(box.cls)
                label = self.names.get(cls, "unknown")
                fire_detected = True
                label_text = f"{str(label).upper()} {conf:.2f}"

                (tw, th), _ = cv2.getTextSize(
                    label_text,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, 2
                )
                cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 10, y1), (0, 0, 255), -1)
                cv2.putText(frame, label_text, (x1 + 5, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            if fire_detected:
                cv2.putText(frame, "FIRE / SMOKE ALERT!", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            return frame, fire_detected

        # Preprocess
        blob = cv2.dnn.blobFromImage(
            frame,
            1/255.0,
            (self.input_size, self.input_size),
            swapRB=True,
            crop=False
        )

        self.net.setInput(blob)
        outputs = self.net.forward()

        # Normalize output shape to (N, D)
        if outputs.ndim == 3:
            dets = outputs[0]
            if dets.shape[0] <= dets.shape[1]:
                dets = dets.T
        elif outputs.ndim == 2:
            dets = outputs
        else:
            dets = np.zeros((0, 6), dtype=np.float32)

        boxes = []
        confidences = []
        class_ids = []

        for det in dets:
            if len(det) < 6:
                continue

            x, y, w_box, h_box = det[0], det[1], det[2], det[3]
            num_classes = len(self.names)

            # Handle both "no objectness" (4+nc) and "with objectness" (5+nc)
            if len(det) == 4 + num_classes:
                scores = det[4:]
            elif len(det) == 5 + num_classes:
                obj = det[4]
                scores = det[5:] * obj
            else:
                scores = det[4:]

            cls = int(np.argmax(scores))
            conf = float(scores[cls])

            if conf < self.conf_threshold:
                continue

            x1 = int((x - w_box / 2) * w / self.input_size)
            y1 = int((y - h_box / 2) * h / self.input_size)
            x2 = int((x + w_box / 2) * w / self.input_size)
            y2 = int((y + h_box / 2) * h / self.input_size)

            # Clamp to frame bounds and skip invalid boxes
            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(0, min(x2, w - 1))
            y2 = max(0, min(y2, h - 1))
            if x2 <= x1 or y2 <= y1:
                continue

            boxes.append([x1, y1, x2 - x1, y2 - y1])
            confidences.append(conf)
            class_ids.append(cls)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, 0.45)

        # Fallback to legacy parsing if NMS returns nothing
        if not len(indices) and len(dets):
            for det in dets:
                x, y, w_box, h_box = det[0], det[1], det[2], det[3]
                scores = det[4:]
                cls = int(np.argmax(scores))
                conf = float(scores[cls])
                if conf < self.conf_threshold:
                    continue
                x1 = int((x - w_box / 2) * w / self.input_size)
                y1 = int((y - h_box / 2) * h / self.input_size)
                x2 = int((x + w_box / 2) * w / self.input_size)
                y2 = int((y + h_box / 2) * h / self.input_size)
                x1 = max(0, min(x1, w - 1))
                y1 = max(0, min(y1, h - 1))
                x2 = max(0, min(x2, w - 1))
                y2 = max(0, min(y2, h - 1))
                if x2 <= x1 or y2 <= y1:
                    continue
                boxes.append([x1, y1, x2 - x1, y2 - y1])
                confidences.append(conf)
                class_ids.append(cls)
            indices = list(range(len(boxes)))

        if len(indices) > 0:
            fire_detected = True

        for i in indices.flatten() if hasattr(indices, "flatten") else indices:
            x, y, w_box, h_box = boxes[i]
            cls = class_ids[i]
            conf = confidences[i]

            label = self.names.get(cls, "unknown")
            color = (0, 0, 255)
            label_text = f"{label.upper()} {conf:.2f}"

            (tw, th), _ = cv2.getTextSize(
                label_text,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6, 2
            )

            cv2.rectangle(frame, (x, y - th - 10), (x + tw + 10, y), color, -1)
            cv2.putText(frame, label_text, (x + 5, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), color, 2)

        if fire_detected:
            cv2.putText(frame, "FIRE / SMOKE ALERT!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        return frame, fire_detected
