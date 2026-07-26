"""Schema cho User và dữ liệu dinh dưỡng (port từ Nutrition Warrior).

Mô hình dữ liệu giữ nguyên ý tưởng của NW:
    - User lưu các "chỉ số dinh dưỡng" (mục tiêu calo/protein/carb/fat, tdee,
      chiều cao, cân nặng) cùng danh sách `daily_logs` nhúng.
    - Mỗi DailyLog ghi lượng nạp vào (intake) và lượng còn lại (remain) trong
      ngày, kèm các bữa ăn breakfast/lunch/dinner.
"""

from pydantic import BaseModel, EmailStr, Field

# Khoá dinh dưỡng dùng chung với model nhận diện / Edamam (giống NW).
DEFAULT_NUTRIENTS = {
    "ENERC_KCAL": 0.0,  # calo
    "PROCNT": 0.0,      # protein
    "FAT": 0.0,         # chất béo
    "CHOCDF": 0.0,      # carb
    "FIBTG": 0.0,       # chất xơ
}


class Food(BaseModel):
    """Một món ăn được thêm vào nhật ký bữa ăn."""

    foodId: str | None = None
    label: str | None = None
    knownAs: str | None = None
    nutrients: dict[str, float] = Field(default_factory=lambda: dict(DEFAULT_NUTRIENTS))
    category: str | None = None
    categoryLabel: str | None = None
    image: str | None = None
    # Khẩu phần đã ghi, để nhật ký hiển thị lại đúng lượng người dùng đã chọn.
    # Món tính theo gram (scan / tìm kiếm) dùng `serving_grams`; món tính theo
    # khẩu phần (recipe) dùng `servings`. Phải khai báo ở đây, nếu không
    # Pydantic sẽ loại bỏ chúng khỏi payload trước khi lưu.
    serving_grams: float | None = None
    servings: float | None = None


# ---------- Input cho các endpoint auth ----------
class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_number: str | None = None
    gender: str | None = None
    date_of_birth: str | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UpdateUserIn(BaseModel):
    """Cập nhật thông tin hồ sơ. Mọi field đều tuỳ chọn."""

    name: str | None = None
    phone_number: str | None = None
    address: str | None = None
    gender: str | None = None
    date_of_birth: str | None = None
    profile_picture: str | None = None
    image: str | None = None


class UpdateHeightWeightIn(BaseModel):
    height: float | None = None
    current_weight: float | None = None
