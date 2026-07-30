"""Schema cho tính năng nhận diện nguyên liệu."""

from typing import Literal

from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str
    confidence: float
    count: int
    # Mô hình nào đã phát hiện vật này: "model_120" (bản tự huấn luyện), "model_nw"
    # (Nutrition-Warrior), "coco" (YOLO11n gốc). Một vật có thể được nhiều mô hình
    # cùng thấy; nhãn cuối cùng là nhãn của mô hình có độ tin cậy cao nhất.
    sources: list[str] = []
    estimated_grams: float | None = None
    estimation_method: Literal["reference_scaled", "count_fallback", "not_applicable"]
    # Dinh dưỡng per-100g tra từ Edamam (keys: ENERC_KCAL/PROCNT/FAT/CHOCDF/FIBTG).
    nutrients_per_100g: dict[str, float] | None = None
    # Dinh dưỡng thực của khẩu phần (per-100g x estimated_grams). None nếu chưa
    # ước lượng được gram hoặc không tra được dữ liệu dinh dưỡng.
    nutrients: dict[str, float] | None = None


class DetectionOut(BaseModel):
    ingredients: list[Ingredient]
    reference_object: str | None = None
