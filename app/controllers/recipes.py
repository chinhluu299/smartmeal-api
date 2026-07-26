"""Controller gợi ý món ăn theo nguyên liệu (Spoonacular)."""

from fastapi import APIRouter, HTTPException

from ..schemas.recipe import RecipeDetail, RecipeSuggestIn, RecipeSuggestOut
from ..services import recipe as service
from ..services.recipe import RecipeError

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("/suggest", response_model=RecipeSuggestOut)
def suggest_recipes(data: RecipeSuggestIn):
    try:
        recipes = service.suggest_by_ingredients(data.ingredients, data.number)
    except RecipeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return {"recipes": recipes}


@router.get("/{recipe_id}", response_model=RecipeDetail)
def get_recipe(recipe_id: int):
    try:
        return service.get_recipe_detail(recipe_id)
    except RecipeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
