"""Schema cho thao tác trên nhật ký dinh dưỡng theo ngày (daily log)."""

from typing import Literal

from pydantic import BaseModel

from .user import Food


class AddFoodIn(BaseModel):
    """Thêm một món ăn vào bữa ăn của một ngày."""

    food_item: Food
    meal: Literal["breakfast", "lunch", "dinner"]


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
