"""Service nhận diện nguyên liệu trong ảnh bằng YOLO.

Ngoài detect nguyên liệu (model fine-tune `best.pt`), còn ước lượng khối
lượng (gram) bằng cách chạy thêm model gốc chưa fine-tune `reference.pt`
(vẫn giữ 80 class MS-COCO) để tìm vật có kích thước thật khá chuẩn (thìa,
nĩa, dao, cốc, bát) làm mốc quy đổi tỷ lệ pixel -> cm trong cùng bức ảnh.

Đây là ƯỚC LƯỢNG heuristic (giả định vật tham chiếu cùng mặt phẳng/khoảng
cách camera với nguyên liệu, giả định hình dạng phẳng đều), không phải phép
đo chính xác.
"""

import numpy as np
import cv2
from ultralytics import YOLO

from ..core.config import settings

_model = YOLO(str(settings.MODEL_PATH))
_ref_model = YOLO(str(settings.REFERENCE_MODEL_PATH))

# Kích thước thật trung bình (cm, cạnh dài nhất) của vật tham chiếu dùng để
# quy đổi tỷ lệ. Ưu tiên dao/thìa/nĩa vì kích thước chuẩn hơn cốc/bát.
REFERENCE_OBJECTS_CM = {
    "fork": 19.5,
    "knife": 21.5,
    "spoon": 18.0,
    "cup": 8.0,
    "bowl": 15.0,
}
REFERENCE_PRIORITY = ["fork", "knife", "spoon", "cup", "bowl"]

# 24 class nguyên liệu thô trong `best.pt` (35 class còn lại là món đã nấu,
# không quy đổi khối lượng vì không map được sang mô hình hình dạng/khối
# lượng của nguyên liệu rời).
AVERAGE_UNIT_WEIGHT_G = {
    "Bitter melon": 200,
    "Brinjal": 200,
    "Cabbage": 900,
    "Calabash": 500,
    "Capsicum": 120,
    "Cauliflower": 600,
    "Garlic": 40,
    "Ginger": 15,
    "Green Chili": 5,
    "Lady finger": 10,
    "Onion": 110,
    "Potato": 170,
    "Sponge Gourd": 150,
    "Tomato": 123,
    "apple": 180,
    "banana": 120,
    "cucumber": 300,
    "dragon fruit": 350,
    "guava": 150,
    "orange": 180,
    "oren": 180,
    "pear": 178,
    "pineapple": 900,
    "sugar apple": 150,
}
DEFAULT_UNIT_WEIGHT_G = 150

# Hồ sơ hình dạng dùng khi CÓ vật tham chiếu (area_cm2 -> gram). MVP: 1 profile
# mặc định chung cho mọi nguyên liệu thô, dễ tách riêng từng class sau.
SHAPE_THICKNESS_CM = 3.0
SHAPE_DENSITY_G_CM3 = 0.6


def _decode(image_bytes: bytes):
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Ảnh không hợp lệ")
    return img


def detect(image_bytes: bytes, conf: float = settings.DEFAULT_CONF):
    """Nhận diện nguyên liệu trong ảnh, trả về danh sách đã gộp theo tên
    (kèm tổng diện tích bbox `area_px` để phục vụ ước lượng khối lượng)."""
    img = _decode(image_bytes)
    result = _model.predict(img, conf=conf, verbose=False)[0]

    items = {}
    for box in result.boxes:
        name = _model.names[int(box.cls)]
        score = float(box.conf)
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        area = max(0.0, x2 - x1) * max(0.0, y2 - y1)

        cur = items.get(name)
        if cur is None or score > cur["confidence"]:
            items[name] = {"name": name, "confidence": round(score, 3)}
        items[name]["count"] = items[name].get("count", 0) + 1
        items[name]["area_px"] = items[name].get("area_px", 0.0) + area

    return sorted(items.values(), key=lambda x: x["confidence"], reverse=True)


def _find_reference_scale(img, conf: float = 0.25):
    """Tìm vật tham chiếu có độ tin cậy cao nhất theo thứ tự ưu tiên.

    Trả về (tên_vật, cm_per_px) hoặc None nếu không thấy vật nào phù hợp.
    """
    result = _ref_model.predict(img, conf=conf, verbose=False)[0]

    best = None  # (priority_index, confidence, name, pixel_len)
    for box in result.boxes:
        name = _ref_model.names[int(box.cls)]
        if name not in REFERENCE_OBJECTS_CM:
            continue
        score = float(box.conf)
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        pixel_len = max(x2 - x1, y2 - y1)
        if pixel_len <= 0:
            continue
        priority = REFERENCE_PRIORITY.index(name)
        candidate = (priority, -score, name, pixel_len)
        if best is None or candidate < best:
            best = candidate

    if best is None:
        return None
    _, neg_score, name, pixel_len = best
    return name, REFERENCE_OBJECTS_CM[name] / pixel_len


def estimate_portions(image_bytes: bytes, conf: float = settings.DEFAULT_CONF) -> dict:
    """Detect nguyên liệu + ước lượng khối lượng (gram) từng loại.

    Ưu tiên quy đổi theo vật tham chiếu nếu có trong ảnh; nếu không, fallback
    về ước lượng thô theo số lượng x trọng lượng trung bình 1 đơn vị. Với
    class là món đã nấu (không thuộc `AVERAGE_UNIT_WEIGHT_G`), không ước
    lượng (không có mô hình khối lượng phù hợp).
    """
    img = _decode(image_bytes)
    ingredients = detect(image_bytes, conf=conf)
    ref = _find_reference_scale(img)
    reference_object, cm_per_px = ref if ref else (None, None)

    for item in ingredients:
        name = item["name"]
        if name not in AVERAGE_UNIT_WEIGHT_G:
            item["estimated_grams"] = None
            item["estimation_method"] = "not_applicable"
        elif cm_per_px is not None:
            area_cm2 = item.get("area_px", 0.0) * (cm_per_px ** 2)
            item["estimated_grams"] = round(
                area_cm2 * SHAPE_THICKNESS_CM * SHAPE_DENSITY_G_CM3, 1
            )
            item["estimation_method"] = "reference_scaled"
        else:
            weight = AVERAGE_UNIT_WEIGHT_G.get(name, DEFAULT_UNIT_WEIGHT_G)
            item["estimated_grams"] = round(item["count"] * weight, 1)
            item["estimation_method"] = "count_fallback"
        item.pop("area_px", None)

    return {"ingredients": ingredients, "reference_object": reference_object}
