from fastapi import APIRouter, HTTPException

from ..schemas.macro import (
    ExpenditureIn,
    ExpenditureOut,
    MacrosIn,
    MacrosOut,
    UpdateExpenditureIn,
)
from ..services import user as user_service
from ..services.macro import calculate_macros, calculate_tdee
from ..services.user import UserError

router = APIRouter(prefix="/macro", tags=["macro"])


@router.post("/calculate-expenditure/method-1", response_model=ExpenditureOut)
def calculate_expenditure_method_1(data: ExpenditureIn):
    try:
        tdee = calculate_tdee(data.weight, data.activity_level)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"tdee": tdee}


@router.post("/calculate-macros", response_model=MacrosOut)
def calculate_macros_endpoint(data: MacrosIn):
    """Tính mục tiêu macro từ TDEE + mục tiêu tập luyện (không lưu DB)."""
    try:
        return calculate_macros(
            data.goal,
            data.weight,
            data.tdee,
            overweight=data.overweight,
            daily_protein_per_kg=data.daily_protein_per_kg,
            daily_protein_for_overweight_people=data.daily_protein_for_overweight_people,
            daily_fat_percentage=data.daily_fat_percentage,
            deficit_percentage=data.deficit_percentage,
            surplus_percentage=data.surplus_percentage,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/update-expenditure/{user_id}")
def update_expenditure(user_id: str, data: UpdateExpenditureIn):
    """Lưu các chỉ số dinh dưỡng đã chốt (TDEE, goal, macro goals) lên user."""
    try:
        user = user_service.update_expenditure(user_id, data.model_dump())
        return {
            "success": True,
            "message": "Expenditure updated successfully",
            "data": user,
        }
    except UserError as e:
        return {"success": False, "message": e.message}
