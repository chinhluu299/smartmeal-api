"""Schema cho tính năng macro / TDEE."""

from pydantic import BaseModel


class ExpenditureIn(BaseModel):
    gender: str | None = None
    height: float | None = None
    weight: float
    activity_level: str


class ExpenditureOut(BaseModel):
    tdee: float


class MacrosIn(BaseModel):
    goal: str  # "Lose Fat" | "Maintain" | "Gain Muscle"
    weight: float
    tdee: float
    overweight: bool = False
    daily_protein_per_kg: float = 1.8
    daily_protein_for_overweight_people: float = 0.0
    daily_fat_percentage: float = 25.0
    deficit_percentage: float = 0.0
    surplus_percentage: float = 0.0


class MacrosOut(BaseModel):
    goal: str
    caloric_intake_goal: float
    daily_protein_goal: float
    daily_fat_goal: float
    daily_carb_goal: float


class UpdateExpenditureIn(BaseModel):
    tdee: float | None = None
    goal: str | None = None
    age: int | None = None
    current_weight: float | None = None
    height: float | None = None
    caloric_intake_goal: float | None = None
    daily_protein_goal: float | None = None
    daily_fat_goal: float | None = None
    daily_carb_goal: float | None = None
    # Nếu gửi kèm, sẽ đồng bộ mục tiêu vào log của ngày đó (YYYY-MM-DD).
    date: str | None = None
