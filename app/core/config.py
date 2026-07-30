"""Cấu hình tập trung cho ứng dụng."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Thư mục gốc của project (smartmeal-api/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Nạp biến môi trường từ file .env ở thư mục gốc.
# override=True: giá trị trong .env luôn thắng biến môi trường có sẵn (tránh
# trường hợp giá trị cũ/sai còn kẹt trong process khi --reload).
load_dotenv(BASE_DIR / ".env", override=True)


class Settings:
    APP_NAME: str = "SmartMeal API"
    APP_VERSION: str = "1.0.0"

    # Model nhận diện nguyên liệu chính: 120 class, bản tự huấn luyện mới nhất.
    MODEL_PATH: Path = BASE_DIR / "model" / "best.pt"
    DEFAULT_CONF: float = float(os.getenv("DETECT_CONF", "0.25"))

    # Model của dự án Nutrition-Warrior (YOLOv8n, 90 class). Chạy song song vì
    # phủ được nhóm trái cây phổ thông, nhóm món phương Tây và 10 MÓN VIỆT
    # (phở, bánh mì, bún bò Huế, cơm tấm...) mà bộ 120 class không có.
    NW_MODEL_PATH: Path = BASE_DIR / "model" / "nw-90class.pt"

    # Model gốc (chưa fine-tune, còn giữ 80 class MS-COCO) - dùng cho 2 việc:
    # tìm vật tham chiếu (thìa/nĩa/dao/cốc/bát) để quy đổi tỷ lệ pixel -> cm,
    # và bổ sung 10 class thực phẩm của COCO.
    REFERENCE_MODEL_PATH: Path = BASE_DIR / "model" / "reference.pt"

    # ExerciseDB (RapidAPI) - dùng cho module tập luyện
    EXERCISEDB_BASE_URL: str = "https://exercisedb.p.rapidapi.com"
    RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
    RAPIDAPI_HOST: str = os.getenv("RAPIDAPI_HOST", "exercisedb.p.rapidapi.com")

    # Spoonacular - gợi ý món ăn theo nguyên liệu (module recipes)
    SPOONACULAR_BASE_URL: str = "https://api.spoonacular.com"
    SPOONACULAR_API_KEY: str = os.getenv("SPOONACULAR_API_KEY", "")

    # Edamam Nutrition Analysis API - tra cứu dinh dưỡng nguyên liệu sau khi
    # detect. Nhận chuỗi kiểu "100 g apple", trả 5 chỉ số per-100g:
    # ENERC_KCAL / PROCNT / FAT / CHOCDF / FIBTG.
    EDAMAM_BASE_URL: str = "https://api.edamam.com"
    EDAMAM_APP_ID: str = os.getenv("EDAMAM_APP_ID", "")
    EDAMAM_APP_KEY: str = os.getenv("EDAMAM_APP_KEY", "")

    # MongoDB - cache dữ liệu ExerciseDB để khỏi gọi RapidAPI (có giới hạn/tháng)
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "smartmeal")


settings = Settings()
