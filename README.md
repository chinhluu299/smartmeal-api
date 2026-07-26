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
# Bind 0.0.0.0 để điện thoại / emulator cùng mạng có thể kết nối
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Mở docs: http://127.0.0.1:8000/docs

> App mobile cấu hình host backend trong `smartmeal/api/axiosClient.js`
> (mặc định IP LAN, hoặc đặt biến `EXPO_PUBLIC_API_URL`). Thiết bị thật phải
> cùng Wi-Fi với máy chạy backend.

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
