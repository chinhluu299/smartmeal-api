"""Service nhận diện nguyên liệu trong ảnh bằng YOLO.

Chạy ĐỒNG THỜI 3 mô hình trên cùng một ảnh rồi hợp nhất kết quả, để bắt được
nhiều vật thể hơn so với dùng một mô hình:

1. `best.pt`       — 120 lớp nguyên liệu, bản tự huấn luyện (100 epoch). Mạnh ở
   nguyên liệu thô: rau củ, đậu, thịt cá, gia vị.
2. `nw-90class.pt` — 90 lớp, mô hình của dự án Nutrition-Warrior. Phủ trái cây phổ
   thông, món phương Tây, hải sản và 10 món Việt (phở, bánh mì, bún bò Huế...).
3. `reference.pt`  — YOLO11n gốc, 80 lớp MS-COCO. Dùng cho 2 việc: tìm vật có kích
   thước thật khá chuẩn (thìa, nĩa, dao, cốc, bát) làm mốc quy đổi tỷ lệ
   pixel -> cm, và bổ sung 10 lớp thực phẩm của COCO.

Tên lớp của 3 mô hình được đưa về một bộ tên chung (`labels.canonical`) trước khi
gộp, nếu không thì cùng một quả táo sẽ hiện ra 3 dòng ("Apple" / "Apple" /
"apple").

QUYẾT ĐỊNH NHÃN THEO ĐIỂM SỐ: khi nhiều mô hình cùng bắt được một vật (khung bao
chồng nhau quá `MERGE_IOU`), nhãn của khung có ĐỘ TIN CẬY CAO NHẤT được chọn, các
nhãn còn lại bị loại. Vừa để một vật không bị đếm thành nhiều lần, vừa để mô hình
nào "chắc" nhất về vật đó thì quyết định vật đó là gì.

Ước lượng khối lượng là ƯỚC LƯỢNG heuristic (giả định vật tham chiếu cùng mặt
phẳng/khoảng cách camera với nguyên liệu, giả định hình dạng phẳng đều), không
phải phép đo chính xác.
"""

import numpy as np
import cv2
from ultralytics import YOLO

from ..core.config import settings
from .labels import COCO_FOOD_CLASSES, GENERIC_CLASSES, canonical, display

_model = YOLO(str(settings.MODEL_PATH))
_nw_model = YOLO(str(settings.NW_MODEL_PATH))
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

# Ngưỡng riêng cho việc tìm vật tham chiếu: giữ cố định, không đi theo `conf` của
# lời gọi, để người dùng nâng ngưỡng nhận diện nguyên liệu không làm mất luôn mốc
# quy đổi kích thước.
REFERENCE_CONF = 0.25

# Hai khung bao của 2 mô hình khác nhau chồng nhau quá mức này thì coi như cùng
# một vật -> chỉ giữ khung có độ tin cậy cao nhất.
MERGE_IOU = 0.65

# Khối lượng trung bình (gram) của 1 quả/củ/cây, theo BỘ TÊN CHUNG ở labels.py.
# Dùng cho nhánh ước lượng thô khi ảnh không có vật tham chiếu.
#
# Dict này đồng thời là DANH SÁCH TRẮNG cho cả hai nhánh ước lượng: lớp không có
# trong đây thì `estimated_grams = None`. Những nhóm bị loại có chủ ý vì không có
# khái niệm "1 đơn vị" rõ ràng, đếm số khung bao rồi nhân lên sẽ ra số vô nghĩa:
#   - gia vị / chất lỏng: muối, đường, bột ớt, quế, dầu, nước tương, sốt, sữa, bơ
#   - đậu / hạt / ngũ cốc dạng đống rời: các loại lentils, beans, gạo, lúa mì
#   - rau lá dạng bó/mớ: các loại saag, rau bina, lá khoai, gundruk
#   - thịt cá cắt miếng và món đã chế biến: bò, lợn, gà, cá, hải sản, bánh mì, mì,
#     kimchi, pizza, burger... và cả 10 món Việt — khẩu phần các món này thay đổi
#     quá nhiều theo cách nấu, đếm số đĩa rồi nhân lên sẽ sai rất xa
#   - quả quá lớn, thực tế luôn dùng theo miếng: dưa hấu, mít, bí đỏ, bí xanh
AVERAGE_UNIT_WEIGHT_G = {
    "apple": 180,
    "artichoke": 130,
    "asparagus": 16,
    "avocado": 200,
    "banana": 120,
    "beetroot": 130,
    "bell pepper": 120,
    "bitter gourd": 200,
    "bottle gourd": 800,
    "broccoli": 450,
    "cabbage": 900,
    "carrot": 60,
    "cassava": 400,
    "cauliflower": 600,
    "chayote": 200,
    "chili pepper": 5,
    "corn": 150,
    "cucumber": 300,
    "egg": 50,
    "eggplant": 200,
    "fig": 50,
    "garlic": 40,
    "ginger": 15,
    "grapefruit": 250,
    "hog plum": 20,
    "lemon": 60,
    "lime": 45,
    "mango": 200,
    "moringa drumsticks": 25,
    "mushroom": 20,
    "okra": 10,
    "onion": 110,
    "orange": 180,
    "papaya": 500,
    "peach": 150,
    "pear": 178,
    "pineapple": 900,
    "pointed gourd": 40,
    "pomegranate": 280,
    "potato": 170,
    "radish": 100,
    "red chili pepper": 8,
    "ridge gourd": 150,
    "snake gourd": 400,
    "strawberry": 12,
    "sweet potato": 130,
    "tamarillo": 60,
    "taro root": 100,
    "tomato": 123,
    "turnip": 120,
    "zucchini": 200,
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


def _iou(a: tuple, b: tuple) -> float:
    """Tỷ lệ chồng lấn (intersection over union) của 2 khung bao xyxy."""
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    if inter <= 0:
        return 0.0
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _boxes_of(model, img, conf: float, source: str):
    """Chạy 1 mô hình, trả các phát hiện đã chuẩn hoá tên về bộ tên chung."""
    out = []
    for b in model.predict(img, conf=conf, verbose=False)[0].boxes:
        raw = model.names[int(b.cls)]
        if raw in GENERIC_CLASSES:
            continue
        out.append({
            "key": canonical(raw),
            "confidence": float(b.conf),
            "xyxy": tuple(b.xyxy[0].tolist()),
            "source": source,
        })
    return out


def _merge_overlaps(dets: list[dict]) -> list[dict]:
    """NMS không phân biệt lớp giữa các mô hình — điểm số quyết định nhãn.

    Cùng một vật thường được nhiều mô hình bắt được, và có thể được gán những nhãn
    KHÁC NHAU. Xét lần lượt từ khung có độ tin cậy cao xuống thấp: khung nào chồng
    lên một khung đã giữ thì bị loại, nên nhãn thắng luôn là nhãn của mô hình chắc
    chắn nhất về vật đó. Bước này cũng tránh việc một vật bị đếm thành nhiều lần
    (nếu không lọc, `count` và tổng diện tích sẽ nhân lên, gram sai gấp mấy lần).

    `sources` ghi lại tất cả mô hình đã thấy vật đó, kể cả mô hình bị loại nhãn.
    """
    kept: list[dict] = []
    for det in sorted(dets, key=lambda d: d["confidence"], reverse=True):
        dup = next((k for k in kept if _iou(det["xyxy"], k["xyxy"]) >= MERGE_IOU), None)
        if dup is None:
            det["sources"] = {det["source"]}
            kept.append(det)
        else:
            dup["sources"].add(det["source"])
    return kept


def _group_by_name(dets: list[dict]) -> list[dict]:
    """Gộp các phát hiện theo tên chung, kèm tổng diện tích khung bao."""
    items: dict[str, dict] = {}
    for det in dets:
        key = det["key"]
        x1, y1, x2, y2 = det["xyxy"]
        area = max(0.0, x2 - x1) * max(0.0, y2 - y1)

        item = items.get(key)
        if item is None:
            item = items[key] = {
                "key": key, "name": display(key), "confidence": 0.0,
                "count": 0, "area_px": 0.0, "sources": set(),
            }
        item["confidence"] = max(item["confidence"], det["confidence"])
        item["count"] += 1
        item["area_px"] += area
        item["sources"] |= det["sources"]

    for item in items.values():
        item["confidence"] = round(item["confidence"], 3)
        item["sources"] = sorted(item["sources"])
    return sorted(items.values(), key=lambda x: x["confidence"], reverse=True)


def _reference_scale(ref_boxes):
    """Tìm vật tham chiếu có độ tin cậy cao nhất theo thứ tự ưu tiên.

    Trả về (tên_vật, cm_per_px) hoặc (None, None) nếu không thấy vật phù hợp.
    """
    best = None  # (priority_index, -confidence, name, pixel_len)
    for box in ref_boxes:
        name = _ref_model.names[int(box.cls)]
        if name not in REFERENCE_OBJECTS_CM:
            continue
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        pixel_len = max(x2 - x1, y2 - y1)
        if pixel_len <= 0:
            continue
        candidate = (REFERENCE_PRIORITY.index(name), -float(box.conf), name, pixel_len)
        if best is None or candidate < best:
            best = candidate

    if best is None:
        return None, None
    _, _, name, pixel_len = best
    return name, REFERENCE_OBJECTS_CM[name] / pixel_len


def _detect_all(img, conf: float):
    """Chạy cả 3 mô hình một lượt, trả (danh sách nguyên liệu, vật tham chiếu)."""
    dets = _boxes_of(_model, img, conf, "model_120")
    dets += _boxes_of(_nw_model, img, conf, "model_nw")

    # `reference.pt` chỉ chạy MỘT lần rồi dùng cho cả hai việc: lấy lớp thực phẩm
    # của COCO và tìm vật tham chiếu. Ngưỡng lấy theo REFERENCE_CONF (thấp) rồi
    # mới lọc phần thực phẩm theo `conf` của lời gọi.
    ref_boxes = _ref_model.predict(img, conf=REFERENCE_CONF, verbose=False)[0].boxes
    for box in ref_boxes:
        raw = _ref_model.names[int(box.cls)]
        if raw in COCO_FOOD_CLASSES and float(box.conf) >= conf:
            dets.append({
                "key": canonical(raw),
                "confidence": float(box.conf),
                "xyxy": tuple(box.xyxy[0].tolist()),
                "source": "coco",
            })

    return _group_by_name(_merge_overlaps(dets)), _reference_scale(ref_boxes)


def detect(image_bytes: bytes, conf: float = settings.DEFAULT_CONF):
    """Nhận diện nguyên liệu trong ảnh (hợp nhất 3 mô hình), đã gộp theo tên."""
    ingredients, _ = _detect_all(_decode(image_bytes), conf)
    return ingredients


def estimate_portions(image_bytes: bytes, conf: float = settings.DEFAULT_CONF) -> dict:
    """Detect nguyên liệu + ước lượng khối lượng (gram) từng loại.

    Ưu tiên quy đổi theo vật tham chiếu nếu có trong ảnh; nếu không, fallback về
    ước lượng thô theo số lượng x trọng lượng trung bình 1 đơn vị. Với lớp không
    có trong `AVERAGE_UNIT_WEIGHT_G` (gia vị, chất lỏng, món đã nấu...) thì không
    ước lượng vì không có mô hình khối lượng phù hợp.
    """
    img = _decode(image_bytes)
    ingredients, (reference_object, cm_per_px) = _detect_all(img, conf)

    for item in ingredients:
        key = item["key"]
        if key not in AVERAGE_UNIT_WEIGHT_G:
            item["estimated_grams"] = None
            item["estimation_method"] = "not_applicable"
        elif cm_per_px is not None:
            area_cm2 = item.get("area_px", 0.0) * (cm_per_px ** 2)
            item["estimated_grams"] = round(
                area_cm2 * SHAPE_THICKNESS_CM * SHAPE_DENSITY_G_CM3, 1
            )
            item["estimation_method"] = "reference_scaled"
        else:
            weight = AVERAGE_UNIT_WEIGHT_G.get(key, DEFAULT_UNIT_WEIGHT_G)
            item["estimated_grams"] = round(item["count"] * weight, 1)
            item["estimation_method"] = "count_fallback"
        item.pop("area_px", None)
        item.pop("key", None)

    return {"ingredients": ingredients, "reference_object": reference_object}
