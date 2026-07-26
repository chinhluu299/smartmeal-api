"""Tra cứu thực phẩm theo tên để người dùng tự thêm món vào nhật ký.

Luồng nhập tay (không qua ảnh): gõ tên -> gợi ý danh sách thực phẩm -> chọn 1
món -> lấy dinh dưỡng per-100g -> client nhân theo gram rồi ghi vào daily log.

Nguồn dữ liệu:
  1. **Spoonacular** `/food/ingredients/autocomplete` cho danh sách gợi ý (kèm
     ảnh + đơn vị thường dùng) và `/food/ingredients/{id}/information` với
     `amount=100&unit=grams` cho dinh dưỡng. Chọn Spoonacular vì key Edamam
     hiện tại thuộc loại *Nutrition Analysis*, không gọi được Food Database
     API (`/api/food-database/v2/parser` và `/auto-complete` đều trả 401).
  2. **Edamam Nutrition Analysis** (services/nutrition.py) làm phương án dự
     phòng: tra theo tên tự do, dùng khi Spoonacular không có dinh dưỡng cho
     món đã chọn, hoặc khi người dùng nhập một tên không có trong gợi ý.

Kết quả tra dinh dưỡng được cache in-memory theo id/tên để tiết kiệm quota
(Spoonacular free tier 150 điểm/ngày, dùng chung với module recipes).
"""

import requests

from ..core.config import settings
from . import nutrition

# Ảnh Spoonacular trả về chỉ là tên file -> ghép với CDN để ra URL đầy đủ.
_IMAGE_BASE = "https://img.spoonacular.com/ingredients_250x250/"

# Cache kết quả tra dinh dưỡng. Cache cả trường hợp tra hụt
# (`nutrients_per_100g = None`) để khỏi gọi lại API cho cùng một món.
_by_id_cache: dict[int, dict] = {}
_by_name_cache: dict[str, dict | None] = {}


class FoodError(Exception):
    """Lỗi khi tra cứu thực phẩm, kèm mã HTTP để controller dịch ra response."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _fetch(path: str, params: dict):
    """Gọi Spoonacular, trả JSON. Ném FoodError nếu thiếu key/lỗi mạng."""
    if not settings.SPOONACULAR_API_KEY:
        raise FoodError("SPOONACULAR_API_KEY chưa được cấu hình", 500)
    try:
        response = requests.get(
            f"{settings.SPOONACULAR_BASE_URL}{path}",
            params={**params, "apiKey": settings.SPOONACULAR_API_KEY},
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise FoodError(f"Không gọi được Spoonacular: {e}", 502)
    return response.json()


def _image_url(image: str | None) -> str | None:
    if not image:
        return None
    # Phòng khi Spoonacular đổi sang trả URL đầy đủ.
    if image.startswith("http"):
        return image
    return f"{_IMAGE_BASE}{image}"


def search_foods(query: str, number: int = 12) -> list[dict]:
    """Gợi ý thực phẩm theo tên. Trả danh sách rỗng nếu `query` quá ngắn.

    Chỉ lấy tên + ảnh (không kèm dinh dưỡng) vì dinh dưỡng phải gọi thêm 1
    request cho *mỗi* món - quá tốn quota cho một danh sách gợi ý.
    """
    query = (query or "").strip()
    if len(query) < 2:
        return []

    data = _fetch(
        "/food/ingredients/autocomplete",
        {
            "query": query,
            "number": max(1, min(number, 25)),
            "metaInformation": "true",  # kèm id/ảnh/đơn vị thay vì chỉ chuỗi tên
        },
    )
    return [
        {
            "id": item["id"],
            "name": item.get("name", ""),
            "image": _image_url(item.get("image")),
            "aisle": item.get("aisle"),
            "possibleUnits": item.get("possibleUnits") or [],
        }
        for item in data
        if item.get("id") is not None
    ]


def nutrition_by_id(food_id: int) -> dict:
    """Dinh dưỡng per-100g của một món trong danh sách gợi ý.

    Trả `nutrients_per_100g = None` nếu cả Spoonacular lẫn Edamam đều không có
    dữ liệu - client sẽ chặn không cho ghi nhật ký món đó.
    """
    if food_id in _by_id_cache:
        return _by_id_cache[food_id]

    data = _fetch(
        f"/food/ingredients/{food_id}/information",
        {"amount": 100, "unit": "grams"},
    )
    name = data.get("name") or data.get("originalName") or ""
    # `amount=100&unit=grams` -> nutrients Spoonacular trả về đã là per-100g.
    per_100g = nutrition.from_spoonacular(data)
    if per_100g is None and name:
        # Dự phòng: hỏi Edamam theo tên (có cache riêng trong nutrition.py).
        per_100g = nutrition.nutrients_per_100g(name)

    result = {
        "id": food_id,
        "name": name,
        "image": _image_url(data.get("image")),
        "nutrients_per_100g": per_100g,
        "possibleUnits": data.get("possibleUnits") or [],
    }
    _by_id_cache[food_id] = result
    return result


def nutrition_by_name(name: str) -> dict:
    """Dinh dưỡng per-100g theo tên tự nhập (Edamam Nutrition Analysis).

    Dùng khi món người dùng gõ không có trong gợi ý của Spoonacular.
    """
    name = (name or "").strip()
    if not name:
        raise FoodError("Tên thực phẩm không được để trống", 400)

    key = name.lower()
    if key not in _by_name_cache:
        _by_name_cache[key] = nutrition.nutrients_per_100g(name)

    return {
        "id": None,
        "name": name,
        "image": None,
        "nutrients_per_100g": _by_name_cache[key],
        "possibleUnits": [],
    }
