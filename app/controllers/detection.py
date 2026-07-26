from fastapi import APIRouter, File, HTTPException, UploadFile

from ..core.config import settings
from ..schemas.detection import DetectionOut
from ..services.detector import estimate_portions
from ..services.nutrition import enrich

router = APIRouter(tags=["detection"])


@router.post("/detect", response_model=DetectionOut)
async def detect_ingredients(
    file: UploadFile = File(...), conf: float = settings.DEFAULT_CONF
):
    try:
        result = estimate_portions(await file.read(), conf=conf)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Gắn dinh dưỡng (Edamam) cho từng nguyên liệu detect được.
    result["ingredients"] = enrich(result["ingredients"])
    return result
