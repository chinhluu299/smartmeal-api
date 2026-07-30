"""Controller cho nhật ký dinh dưỡng theo ngày."""

from fastapi import APIRouter

from ..schemas.daily_log import AddFoodIn, AddWorkoutIn, RemoveFoodIn
from ..services import daily_log as service
from ..services.user import UserError

router = APIRouter(prefix="/daily-logs", tags=["daily-logs"])


@router.post("/add-food/{user_id}/{date}")
def add_food_to_daily_log(user_id: str, date: str, data: AddFoodIn):
    """Thêm 1 món vào bữa của ngày `date` (YYYY-MM-DD) cho user `user_id`."""
    try:
        user = service.add_food_to_daily_log(
            user_id, date, data.food_item.model_dump(), data.meal
        )
        return {
            "success": True,
            "message": "Food added to daily log successfully",
            "data": user,
        }
    except UserError as e:
        return {"success": False, "message": e.message}


@router.post("/remove-food/{user_id}/{date}")
def remove_food_from_daily_log(user_id: str, date: str, data: RemoveFoodIn):
    """Xoá 1 món khỏi bữa của ngày `date` (YYYY-MM-DD) cho user `user_id`."""
    try:
        user = service.remove_food_from_daily_log(
            user_id, date, data.meal, data.index, data.label
        )
        return {
            "success": True,
            "message": "Food removed from daily log successfully",
            "data": user,
        }
    except UserError as e:
        return {"success": False, "message": e.message}


@router.post("/add-workout/{user_id}/{date}")
def add_workout_to_daily_log(user_id: str, date: str, data: AddWorkoutIn):
    """Ghi 1 buổi tập đã hoàn thành + calo tiêu hao vào nhật ký ngày `date`."""
    try:
        user = service.add_workout_to_daily_log(
            user_id, date, data.workout.model_dump()
        )
        return {
            "success": True,
            "message": "Workout added to daily log successfully",
            "data": user,
        }
    except UserError as e:
        return {"success": False, "message": e.message}
