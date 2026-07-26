"""Schema cho gợi ý giáo án tập luyện (rule-based)."""

from pydantic import BaseModel


class RecommendIn(BaseModel):
    height: float
    weight: float
    activity_level: str  # "Less Active" | "Not Sure" | "More Active"
    goal: str            # "Lose Fat" | "Gain Muscle" | "Maintain"
    overweight: bool = False
    sex: str | None = None
    age: int | None = None  # tuỳ chọn — có tuổi thì tính được nhịp tim mục tiêu


class SaveScheduleIn(BaseModel):
    """Lưu lịch tập tuần đã gán buổi vào các thứ. `schedule` là dict tự do
    (chứa sessions kèm bài tập lồng nhau) nên không ràng buộc cứng cấu trúc."""

    schedule: dict
