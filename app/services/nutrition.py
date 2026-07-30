"""Tra cứu dinh dưỡng cho nguyên liệu qua Edamam Nutrition Analysis API.

Gọi endpoint `/api/nutrition-data` với chuỗi "100 g <tên>" để lấy 5 chỉ số
dinh dưỡng per-100g (ENERC_KCAL, PROCNT, FAT, CHOCDF, FIBTG). Vì tập class của
model là cố định, kết quả được cache in-memory theo tên để hạn chế số request
(Edamam free tier có giới hạn/tháng).

Sau khi có per-100g, nếu nguyên liệu đã được ước lượng khối lượng
(`estimated_grams`) thì nhân theo gram để ra dinh dưỡng thực của khẩu phần.
"""

import requests

from ..core.config import settings
from .labels import canonical, edamam_query

# 5 chỉ số Edamam trả về, trùng đúng bộ khoá mà schema Food/daily_log đang dùng.
NUTRIENT_KEYS = ("ENERC_KCAL", "PROCNT", "FAT", "CHOCDF", "FIBTG")

# Cache theo tên (lower-case). Giá trị None = đã tra nhưng không có dữ liệu,
# để khỏi gọi lại API cho cùng một tên tra hụt.
_cache: dict[str, dict | None] = {}


def _query_edamam(name: str) -> dict | None:
    """Hỏi Edamam dinh dưỡng của 100g `name`, trả dict 5 chỉ số per-100g
    (hoặc None nếu thiếu key / lỗi mạng / Edamam không nhận diện được tên)."""
    if not (settings.EDAMAM_APP_ID and settings.EDAMAM_APP_KEY):
        return None
    try:
        resp = requests.get(
            f"{settings.EDAMAM_BASE_URL}/api/nutrition-data",
            params={
                "app_id": settings.EDAMAM_APP_ID,
                "app_key": settings.EDAMAM_APP_KEY,
                "ingr": f"100 g {name}",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None

    # Dinh dưỡng nằm trong ingredients[0].parsed[0].nutrients. `parsed` rỗng
    # nghĩa là Edamam không nhận ra tên -> coi như không có dữ liệu.
    ingredients = data.get("ingredients") or []
    parsed = (ingredients[0].get("parsed") if ingredients else None) or []
    if not parsed:
        return None

    nutrients = parsed[0].get("nutrients", {})  # đơn vị: per 100g
    return {
        k: round(float(nutrients.get(k, {}).get("quantity", 0.0)), 2)
        for k in NUTRIENT_KEYS
    }


def nutrients_per_100g(name: str) -> dict | None:
    """Trả dict 5 chỉ số per-100g cho `name` (None nếu không tra được).

    `name` được đưa về bộ tên chung ở `labels.py` trước khi tra: tên lớp thô của
    các mô hình (kèm tên địa phương, tên vùng miền, lỗi chính tả) không phải tên
    thực phẩm mà Edamam nhận diện được. Với món Việt còn phải đổi sang chuỗi mô tả
    tiếng Anh vì Edamam chỉ hỗ trợ tiếng Anh (xem `labels.EDAMAM_QUERY`).
    """
    key = canonical(name)
    if key in _cache:
        return _cache[key]
    result = _query_edamam(edamam_query(key))
    _cache[key] = result
    return result


def _scale(per_100g: dict, grams: float) -> dict:
    factor = grams / 100.0
    return {k: round(v * factor, 2) for k, v in per_100g.items()}


# Tên chất dinh dưỡng của Spoonacular -> bộ khoá Edamam dùng chung ở trên, để
# món ghi từ recipe / tìm kiếm thủ công cộng dồn chung định dạng với món ghi
# từ scan.
SPOON_TO_EDAMAM = {
    "Calories": "ENERC_KCAL",
    "Protein": "PROCNT",
    "Fat": "FAT",
    "Carbohydrates": "CHOCDF",
    "Fiber": "FIBTG",
}


def from_spoonacular(data: dict) -> dict | None:
    """Rút dinh dưỡng từ payload Spoonacular về vocab Edamam.

    `data` là một object có `nutrition.nutrients` (recipe information hoặc
    ingredient information). Đơn vị giữ nguyên theo lượng mà Spoonacular đã
    chuẩn hoá cho payload đó (mỗi khẩu phần với recipe, theo `amount` đã yêu
    cầu với nguyên liệu). Trả None nếu payload không kèm dữ liệu dinh dưỡng.
    """
    nutrients = (data.get("nutrition") or {}).get("nutrients") or []
    if not nutrients:
        return None
    by_name = {n.get("name"): n for n in nutrients}
    out = {}
    for spoon, edamam in SPOON_TO_EDAMAM.items():
        n = by_name.get(spoon)
        if n is not None:
            out[edamam] = round(float(n.get("amount", 0.0)), 2)
    return out or None


def enrich(ingredients: list[dict]) -> list[dict]:
    """Gắn dinh dưỡng vào từng nguyên liệu (mutate tại chỗ và trả lại danh sách).

    - `nutrients_per_100g`: chỉ số per-100g từ Edamam (None nếu không tra được).
    - `nutrients`: chỉ số đã nhân theo `estimated_grams` (None nếu thiếu gram
      hoặc không có per-100g) — đây là dinh dưỡng thực của khẩu phần trong ảnh.
    """
    for item in ingredients:
        per_100g = nutrients_per_100g(item["name"])
        item["nutrients_per_100g"] = per_100g
        grams = item.get("estimated_grams")
        item["nutrients"] = _scale(per_100g, grams) if per_100g and grams else None
    return ingredients
