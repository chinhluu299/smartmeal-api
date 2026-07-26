"""Gom toàn bộ controller của ứng dụng vào một router chung."""

from fastapi import APIRouter

from . import auth, daily_log, detection, exercise, food, health, macro, recipes, workout

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(detection.router)
api_router.include_router(macro.router)
api_router.include_router(exercise.router)
api_router.include_router(auth.router)
api_router.include_router(daily_log.router)
api_router.include_router(food.router)
api_router.include_router(recipes.router)
api_router.include_router(workout.router)
