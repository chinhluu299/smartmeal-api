"""Kết nối MongoDB (pymongo) dùng chung cho ứng dụng.

Client được khởi tạo lazy (chỉ kết nối khi cần) để app vẫn start được dù
MongoDB tạm thời không truy cập được.
"""

import certifi
from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from .config import settings

_client: MongoClient | None = None


def get_client() -> MongoClient:
    """Trả về MongoClient dùng chung (singleton)."""
    global _client
    if _client is None:
        if not settings.MONGODB_URI:
            raise RuntimeError(
                "MONGODB_URI chưa được cấu hình. Hãy điền vào file .env."
            )
        _client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=10000,
            tlsCAFile=certifi.where(),
        )
    return _client


def get_db() -> Database:
    return get_client()[settings.MONGODB_DB_NAME]


def get_exercises_collection() -> Collection:
    return get_db()["exercises"]


def get_exercise_images_collection() -> Collection:
    """Cache ảnh GIF của bài tập (binary) để khỏi gọi lại RapidAPI."""
    return get_db()["exercise_images"]


def get_users_collection() -> Collection:
    """Người dùng + chỉ số dinh dưỡng + nhật ký theo ngày (port từ NW)."""
    return get_db()["users"]


def ensure_indexes() -> None:
    """Tạo index phục vụ truy vấn (idempotent)."""
    col = get_exercises_collection()
    col.create_index([("name", ASCENDING)])
    col.create_index([("bodyPart", ASCENDING)])
    col.create_index([("equipment", ASCENDING)])
    col.create_index([("target", ASCENDING)])
    # Phục vụ fallback ảnh: tìm ảnh theo exerciseId không phụ thuộc resolution
    get_exercise_images_collection().create_index([("exerciseId", ASCENDING)])
    # Email là định danh đăng nhập -> không cho trùng
    get_users_collection().create_index([("email", ASCENDING)], unique=True)


def close_client() -> None:
    """Đóng kết nối (gọi khi app shutdown)."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
