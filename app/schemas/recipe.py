"""Schema cho tính năng gợi ý món ăn theo nguyên liệu (Spoonacular)."""

from pydantic import BaseModel


class RecipeSuggestIn(BaseModel):
    ingredients: list[str]
    number: int = 10


class RecipeSuggestion(BaseModel):
    id: int
    title: str
    image: str | None = None
    usedIngredientCount: int
    missedIngredientCount: int
    usedIngredients: list[str]
    missedIngredients: list[str]
    likes: int = 0


class RecipeSuggestOut(BaseModel):
    recipes: list[RecipeSuggestion]


class RecipeDetail(BaseModel):
    id: int
    title: str
    image: str | None = None
    readyInMinutes: int | None = None
    servings: int | None = None
    sourceUrl: str | None = None
    ingredients: list[str]
    steps: list[str]
    # Dinh dưỡng mỗi khẩu phần theo vocab Edamam (ENERC_KCAL/PROCNT/FAT/CHOCDF/
    # FIBTG); None nếu Spoonacular không kèm dữ liệu.
    nutrition: dict[str, float] | None = None
