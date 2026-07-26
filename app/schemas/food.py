"""Schema cho tra cứu thực phẩm theo tên (thêm món thủ công vào nhật ký)."""

from pydantic import BaseModel


class FoodSearchItem(BaseModel):
    """Một gợi ý trong danh sách tìm kiếm (chưa kèm dinh dưỡng)."""

    id: int
    name: str
    image: str | None = None
    aisle: str | None = None
    possibleUnits: list[str] = []


class FoodSearchOut(BaseModel):
    query: str
    foods: list[FoodSearchItem]


class FoodNutritionOut(BaseModel):
    """Dinh dưỡng per-100g của một món; client nhân theo gram người dùng nhập.

    `nutrients_per_100g` là None khi không tra được ở cả Spoonacular lẫn Edamam.
    """

    id: int | None = None
    name: str
    image: str | None = None
    nutrients_per_100g: dict[str, float] | None = None
    possibleUnits: list[str] = []
