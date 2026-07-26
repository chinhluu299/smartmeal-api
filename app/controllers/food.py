"""Controller tra cứu thực phẩm theo tên (Spoonacular + Edamam dự phòng)."""

from fastapi import APIRouter, HTTPException, Query

from ..schemas.food import FoodNutritionOut, FoodSearchOut
from ..services import food as service
from ..services.food import FoodError

router = APIRouter(prefix="/foods", tags=["foods"])


@router.get("/search", response_model=FoodSearchOut)
def search_foods(
    q: str = Query(..., description="Tên thực phẩm cần tìm"),
    number: int = Query(12, ge=1, le=25),
):
    try:
        foods = service.search_foods(q, number)
    except FoodError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return {"query": q, "foods": foods}


@router.get("/nutrition-by-name", response_model=FoodNutritionOut)
def get_nutrition_by_name(name: str = Query(..., description="Tên thực phẩm tự nhập")):
    """Tra dinh dưỡng cho tên không có trong danh sách gợi ý."""
    try:
        return service.nutrition_by_name(name)
    except FoodError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# Đặt sau các route tĩnh ở trên để "search"/"nutrition-by-name" không bị
# khớp nhầm vào path param.
@router.get("/{food_id}/nutrition", response_model=FoodNutritionOut)
def get_food_nutrition(food_id: int):
    try:
        return service.nutrition_by_id(food_id)
    except FoodError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
