# SmartMeal API

Backend FastAPI nhận diện nguyên liệu thực phẩm từ ảnh (model YOLO11 đã train).

## Cài đặt

```bash
cd smartmeal-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Chạy

```bash
uvicorn app.main:app --reload
```

Mở docs: http://127.0.0.1:8000/docs

## API

- `GET /health` — kiểm tra trạng thái.
- `POST /detect` — upload ảnh (`file`), trả về danh sách nguyên liệu nhận diện được.

```bash
curl -F "file=@anh.jpg" http://127.0.0.1:8000/detect
```

```json
{
  "ingredients": [
    { "name": "Tomato", "confidence": 0.91, "count": 2 }
  ]
}
```

## Tiếp theo

Từ danh sách nguyên liệu → gợi ý món ăn & cách nấu (sẽ bổ sung).
