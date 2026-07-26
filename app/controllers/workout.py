"""Controller gợi ý giáo án tập luyện theo hiện trạng cơ thể (rule-based).

Cơ sở lý thuyết + trích dẫn: xem thư mục `theory/`.
"""

from fastapi import APIRouter, HTTPException

from ..schemas.workout import RecommendIn, SaveScheduleIn
from ..services import workout as service
from ..services.user import UserError

router = APIRouter(prefix="/workout", tags=["workout"])


@router.post("/recommend")
def recommend(data: RecommendIn):
    """Sinh giáo án tuần dựa trên chỉ số cơ thể + mục tiêu (không lưu DB)."""
    try:
        plan = service.recommend_plan(
            height_cm=data.height,
            weight_kg=data.weight,
            activity_level=data.activity_level,
            goal=data.goal,
            overweight=data.overweight,
            sex=data.sex,
            age=data.age,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "data": plan}


@router.post("/schedule/{user_id}")
def save_schedule(user_id: str, data: SaveScheduleIn):
    """Lưu lịch tập tuần (đã gán buổi vào các thứ) vào tài khoản user."""
    try:
        user = service.save_schedule(user_id, data.schedule)
        return {"success": True, "message": "Đã lưu lịch tập", "data": user}
    except UserError as e:
        return {"success": False, "message": e.message}
