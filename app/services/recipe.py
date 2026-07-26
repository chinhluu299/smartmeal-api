"""Service gợi ý món ăn theo nguyên liệu (Spoonacular).

Dùng endpoint `findByIngredients` (xếp hạng theo số nguyên liệu khớp) và
`/{id}/information` để lấy chi tiết cách nấu. Không cache trong MongoDB -
free tier Spoonacular (150 request/ngày) đủ dùng cho quy mô hiện tại.
"""

import requests

from ..core.config import settings
from . import nutrition


class RecipeError(Exception):
    """Lỗi khi gọi Spoonacular, kèm mã HTTP để controller dịch ra response."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _fetch(path: str, params: dict):
    """Gọi Spoonacular, trả JSON. Ném RecipeError nếu thiếu key/lỗi mạng."""
    if not settings.SPOONACULAR_API_KEY:
        raise RecipeError("SPOONACULAR_API_KEY chưa được cấu hình", 500)
    try:
        response = requests.get(
            f"{settings.SPOONACULAR_BASE_URL}{path}",
            params={**params, "apiKey": settings.SPOONACULAR_API_KEY},
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RecipeError(f"Không gọi được Spoonacular: {e}", 502)
    return response.json()


def suggest_by_ingredients(ingredients: list[str], number: int = 10) -> list[dict]:
    """Gợi ý recipe xếp hạng theo số nguyên liệu (trong `ingredients`) khớp được."""
    data = _fetch(
        "/recipes/findByIngredients",
        {
            "ingredients": ",".join(ingredients),
            "number": number,
            "ranking": 2,  # tối đa hoá số nguyên liệu đã có được dùng
            "ignorePantry": "true",  # bỏ qua muối/dầu/nước... (model cũng không detect các thứ này)
        },
    )
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "image": r.get("image"),
            "usedIngredientCount": r.get("usedIngredientCount", 0),
            "missedIngredientCount": r.get("missedIngredientCount", 0),
            "usedIngredients": [i["name"] for i in r.get("usedIngredients", [])],
            "missedIngredients": [i["name"] for i in r.get("missedIngredients", [])],
            "likes": r.get("likes", 0),
        }
        for r in data
    ]


def get_recipe_detail(recipe_id: int) -> dict:
    data = _fetch(f"/recipes/{recipe_id}/information", {"includeNutrition": "true"})

    steps: list[str] = []
    for block in data.get("analyzedInstructions", []):
        steps.extend(step["step"] for step in block.get("steps", []))

    return {
        "id": data["id"],
        "title": data["title"],
        "image": data.get("image"),
        "readyInMinutes": data.get("readyInMinutes"),
        "servings": data.get("servings"),
        "sourceUrl": data.get("sourceUrl"),
        "ingredients": [i["original"] for i in data.get("extendedIngredients", [])],
        "steps": steps,
        # Spoonacular đã chuẩn hoá `nutrition.nutrients` theo *mỗi khẩu phần*.
        "nutrition": nutrition.from_spoonacular(data),
    }
