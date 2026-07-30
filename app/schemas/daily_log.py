"""Schema cho thao tác trên nhật ký dinh dưỡng theo ngày (daily log)."""

from typing import Literal

from pydantic import BaseModel, Field

from .user import Food


class AddFoodIn(BaseModel):
    """Thêm một món ăn vào bữa ăn của một ngày."""

    food_item: Food
    meal: Literal["breakfast", "lunch", "dinner"]


class RemoveFoodIn(BaseModel):
    """Xoá một món khỏi bữa ăn của một ngày, theo vị trí trong danh sách."""

    meal: Literal["breakfast", "lunch", "dinner"]
    index: int = Field(ge=0)
    # Tên món client đang hiển thị ở vị trí đó. Không bắt buộc, nhưng nếu có thì
    # server đối chiếu trước khi xoá để không xoá nhầm khi danh sách đã đổi.
    label: str | None = None


class WorkoutLogItem(BaseModel):
    """Một buổi tập đã hoàn thành, ghi vào nhật ký ngày."""

    focus: str
    type: str = "resistance"          # resistance | cardio
    calories_burned: float = 0.0
    minutes: int | None = None
    exercises_count: int | None = None
    key: str | None = None            # định danh để chống ghi trùng (weekday-focus)


class AddWorkoutIn(BaseModel):
    workout: WorkoutLogItem
