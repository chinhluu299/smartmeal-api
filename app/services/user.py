"""Service quản lý người dùng và chỉ số dinh dưỡng.

Port logic lưu trữ user từ Nutrition Warrior (Django + mongoengine) sang
FastAPI + pymongo. Mỗi user là 1 document trong collection `users`, các nhật
ký theo ngày được nhúng vào mảng `daily_logs` y như NW.
"""

from datetime import datetime, timezone

import bcrypt
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

from ..core.database import get_users_collection

# Giá trị mặc định cho các chỉ số dinh dưỡng khi tạo user mới.
_GOAL_DEFAULTS = {
    "caloric_intake_goal": 0.0,
    "daily_protein_goal": 0.0,
    "daily_carb_goal": 0.0,
    "daily_fat_goal": 0.0,
    "goal": "",
    "tdee": 0.0,
    "height": 0.0,
    "current_weight": 0.0,
}


class UserError(Exception):
    """Lỗi nghiệp vụ kèm mã HTTP để controller dịch ra response."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# ---------- Tiện ích nội bộ ----------
def _hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _check_password(raw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, AttributeError):
        return False


def _to_object_id(user_id: str) -> ObjectId:
    try:
        return ObjectId(user_id)
    except (InvalidId, TypeError):
        raise UserError("user_id không hợp lệ", 400)


def serialize_user(doc: dict) -> dict:
    """Chuyển document Mongo thành dict trả về client (ẩn password, _id -> id)."""
    if not doc:
        return {}
    out = dict(doc)
    out["id"] = str(out.pop("_id"))
    out.pop("password", None)
    return out


# ---------- Truy vấn / thao tác ----------
def get_user_by_email(email: str) -> dict | None:
    return get_users_collection().find_one({"email": email})


def get_user_by_id(user_id: str) -> dict:
    doc = get_users_collection().find_one({"_id": _to_object_id(user_id)})
    if not doc:
        raise UserError("User not found", 404)
    return doc


def create_user(data: dict) -> dict:
    """Tạo user mới. `data` đã được Pydantic validate.

    Trả về user vừa tạo (đã serialize). Ném UserError nếu email trùng.
    """
    col = get_users_collection()
    email = data["email"]
    if col.find_one({"email": email}):
        raise UserError("Email already exists", 409)

    doc = {
        "name": data["name"],
        "email": email,
        "password": _hash_password(data["password"]),
        "phone_number": data.get("phone_number"),
        "gender": data.get("gender"),
        "date_of_birth": data.get("date_of_birth"),
        "address": None,
        "profile_picture": None,
        "image": None,
        "daily_logs": [],
        "first_login": True,
        "created_at": datetime.now(timezone.utc),
        **_GOAL_DEFAULTS,
    }
    try:
        result = col.insert_one(doc)
    except DuplicateKeyError:
        raise UserError("Email already exists", 409)
    doc["_id"] = result.inserted_id
    return serialize_user(doc)


def login(email: str, password: str) -> dict:
    user = get_user_by_email(email)
    if not user:
        raise UserError("User not found", 404)
    if not _check_password(password, user.get("password", "")):
        raise UserError("Incorrect password", 401)
    return serialize_user(user)


def get_user_info(email: str) -> dict:
    user = get_user_by_email(email)
    if not user:
        raise UserError("User not found", 404)
    return serialize_user(user)


def update_user(user_id: str, fields: dict) -> dict:
    """Cập nhật các field hồ sơ (bỏ qua field None)."""
    oid = _to_object_id(user_id)
    update = {k: v for k, v in fields.items() if v is not None}
    if not update:
        raise UserError("Không có dữ liệu để cập nhật", 400)
    col = get_users_collection()
    result = col.find_one_and_update(
        {"_id": oid}, {"$set": update}, return_document=True
    )
    if not result:
        raise UserError("User not found", 404)
    return serialize_user(result)


def update_height_weight(user_id: str, height, current_weight) -> dict:
    update = {}
    if height is not None:
        update["height"] = height
    if current_weight is not None:
        update["current_weight"] = current_weight
    if not update:
        raise UserError("Thiếu height/current_weight", 400)
    col = get_users_collection()
    result = col.find_one_and_update(
        {"_id": _to_object_id(user_id)}, {"$set": update}, return_document=True
    )
    if not result:
        raise UserError("User not found", 404)
    serialized = serialize_user(result)
    return {
        "height": serialized.get("height"),
        "current_weight": serialized.get("current_weight"),
    }


# Các field "chỉ số dinh dưỡng" được lưu khi user chốt mục tiêu.
_EXPENDITURE_FIELDS = (
    "tdee",
    "goal",
    "age",
    "current_weight",
    "height",
    "caloric_intake_goal",
    "daily_protein_goal",
    "daily_fat_goal",
    "daily_carb_goal",
)


def update_expenditure(user_id: str, data: dict) -> dict:
    """Lưu mục tiêu dinh dưỡng (TDEE, goal, macro goals) lên user.

    Đồng thời cập nhật mục tiêu + lượng còn lại cho log của ngày `date` (mặc
    định là hôm nay nếu client gửi kèm) nếu log đó đã tồn tại. Tắt cờ
    `first_login`. Bám theo `update_expenditure` của NW.
    """
    user = get_user_by_id(user_id)

    update = {f: data[f] for f in _EXPENDITURE_FIELDS if data.get(f) is not None}
    update["first_login"] = False

    daily_logs = user.get("daily_logs", [])
    target_date = data.get("date")
    if target_date:
        log = next((dl for dl in daily_logs if dl.get("date") == target_date), None)
        if log is not None:
            log["goal"] = update.get("goal", log.get("goal", ""))
            log["caloric_intake_goal"] = update.get("caloric_intake_goal", log.get("caloric_intake_goal", 0.0))
            log["daily_protein_goal"] = update.get("daily_protein_goal", log.get("daily_protein_goal", 0.0))
            log["daily_fat_goal"] = update.get("daily_fat_goal", log.get("daily_fat_goal", 0.0))
            log["daily_carb_goal"] = update.get("daily_carb_goal", log.get("daily_carb_goal", 0.0))
            log["caloric_remain"] = max(0.0, log["caloric_intake_goal"] - log.get("caloric_intake", 0.0))
            log["protein_remain"] = max(0.0, log["daily_protein_goal"] - log.get("protein_intake", 0.0))
            log["carb_remain"] = max(0.0, log["daily_carb_goal"] - log.get("carb_intake", 0.0))
            log["fat_remain"] = max(0.0, log["daily_fat_goal"] - log.get("fat_intake", 0.0))
            update["daily_logs"] = daily_logs

    result = get_users_collection().find_one_and_update(
        {"_id": _to_object_id(user_id)}, {"$set": update}, return_document=True
    )
    return serialize_user(result)
