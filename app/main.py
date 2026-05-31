from fastapi import FastAPI, File, HTTPException, UploadFile

from .detector import detect

app = FastAPI(title="SmartMeal API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect")
async def detect_ingredients(file: UploadFile = File(...), conf: float = 0.25):
    try:
        items = detect(await file.read(), conf=conf)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ingredients": items}
