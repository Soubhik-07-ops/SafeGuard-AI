# CV Model Weights

Model weight files (.pt, .onnx) are excluded from this repository
due to file size constraints (GitHub 100MB limit).

## Required Files

| File | Model | Size | Source |
|------|-------|------|--------|
| `yolo12n.pt` | YOLOv12n Fire & Smoke | ~10MB | Trained on forest-fire dataset |
| `fire_best.onnx` | YOLOv12n Fire & Smoke (ONNX) | ~10MB | Exported from custom model |
| `best.pt` | PPE Compliance | ~16MB | Custom PPE dataset |
| `yolov8m.pt` | Intrusion (person) | ~50MB | Ultralytics pretrained |
| `yolov8n.pt` | Fall/PPE baseline | ~6MB | Ultralytics pretrained |
| `yolov10s.pt` | Fall Detection | ~16MB | Ultralytics pretrained |

## Download Instructions

### YOLOv8 Pretrained Weights
```bash
pip install ultralytics
yolo download model=yolov8m.pt
yolo download model=yolov8n.pt
```

### Fire Detection Model (yolo12n.pt / fire_best.onnx)
Trained custom model — contact the repository owner or
retrain using: `notebooks/smoke_fire_training.ipynb`
