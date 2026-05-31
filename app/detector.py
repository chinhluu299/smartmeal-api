from pathlib import Path

from ultralytics import YOLO

MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "best.pt"

_model = YOLO(str(MODEL_PATH))


def detect(image_bytes: bytes, conf: float = 0.25):
    """Nhận diện nguyên liệu trong ảnh, trả về danh sách đã gộp theo tên."""
    import numpy as np
    import cv2

    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Ảnh không hợp lệ")

    result = _model.predict(img, conf=conf, verbose=False)[0]

    items = {}
    for box in result.boxes:
        name = _model.names[int(box.cls)]
        score = float(box.conf)
        cur = items.get(name)
        if cur is None or score > cur["confidence"]:
            items[name] = {"name": name, "confidence": round(score, 3)}
        items[name]["count"] = items[name].get("count", 0) + 1

    return sorted(items.values(), key=lambda x: x["confidence"], reverse=True)
