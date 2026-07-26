"""Service cho nhật ký dinh dưỡng theo ngày (daily log).

Mỗi user có mảng `daily_logs`. Một log đại diện cho 1 ngày, gồm các bữa
breakfast/lunch/dinner và tổng hợp lượng nạp (intake) / còn lại (remain) so
với mục tiêu dinh dưỡng của user. Logic bám theo `add_food_to_daily_log` của
Nutrition Warrior.
"""

from bson import ObjectId

from ..core.database import get_users_collection
from .user import UserError, serialize_user, get_user_by_id


def _new_daily_log(date: str, user: dict) -> dict:
    """Tạo một log rỗng cho `date`, chốt sẵn mục tiêu theo user hiện tại."""
    return {
        "date": date,
        "caloric_intake": 0.0,
        "protein_intake": 0.0,
        "carb_intake": 0.0,
        "fat_intake": 0.0,
        "caloric_remain": user.get("caloric_intake_goal", 0.0),
        "protein_remain": user.get("daily_protein_goal", 0.0),
        "carb_remain": user.get("daily_carb_goal", 0.0),
        "fat_remain": user.get("daily_fat_goal", 0.0),
        "caloric_intake_goal": user.get("caloric_intake_goal", 0.0),
        "daily_protein_goal": user.get("daily_protein_goal", 0.0),
        "daily_carb_goal": user.get("daily_carb_goal", 0.0),
        "daily_fat_goal": user.get("daily_fat_goal", 0.0),
        "goal": user.get("goal", ""),
        "weight": user.get("current_weight", 0.0),
        "breakfast": [],
        "lunch": [],
        "dinner": [],
        "workouts": [],          # buổi tập đã hoàn thành trong ngày
        "calories_burned": 0.0,  # tổng calo tiêu hao đã ghi nhận
    }


def add_food_to_daily_log(user_id: str, date: str, food_item: dict, meal: str) -> dict:
    """Thêm 1 món vào bữa `meal` của ngày `date`, cập nhật intake/remain.

    Trả về user đã serialize (giống NW: trả nguyên user để client cập nhật state).
    """
    user = get_user_by_id(user_id)
    daily_logs = user.get("daily_logs", [])

    # Tìm log của ngày này, chưa có thì tạo mới.
    log = next((dl for dl in daily_logs if dl.get("date") == date), None)
    if log is None:
        log = _new_daily_log(date, user)
        daily_logs.append(log)

    nutrients = food_item.get("nutrients", {}) or {}
    log[meal].append(food_item)

    # Cộng dồn lượng nạp vào.
    log["caloric_intake"] += nutrients.get("ENERC_KCAL", 0) or 0
    log["protein_intake"] += nutrients.get("PROCNT", 0) or 0
    log["carb_intake"] += nutrients.get("CHOCDF", 0) or 0
    log["fat_intake"] += nutrients.get("FAT", 0) or 0

    # Tính lại lượng còn lại so với mục tiêu (không âm).
    log["caloric_remain"] = max(0.0, user.get("caloric_intake_goal", 0.0) - log["caloric_intake"])
    log["protein_remain"] = max(0.0, user.get("daily_protein_goal", 0.0) - log["protein_intake"])
    log["carb_remain"] = max(0.0, user.get("daily_carb_goal", 0.0) - log["carb_intake"])
    log["fat_remain"] = max(0.0, user.get("daily_fat_goal", 0.0) - log["fat_intake"])

    get_users_collection().update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"daily_logs": daily_logs}}
    )
    user["daily_logs"] = daily_logs
    return serialize_user(user)


def add_workout_to_daily_log(user_id: str, date: str, workout: dict) -> dict:
    """Ghi 1 buổi tập ĐÃ HOÀN THÀNH + calo tiêu hao vào nhật ký ngày `date`.

    Calo tiêu hao được theo dõi RIÊNG (không cộng ngược vào ngân sách calo còn
    lại) vì mục tiêu calo đã tính theo TDEE có hệ số vận động — cộng thêm sẽ đếm
    trùng. Chống ghi trùng theo `key` (vd 'weekday-focus') nếu client gửi kèm.
    Trả về user đã serialize.
    """
    user = get_user_by_id(user_id)
    daily_logs = user.get("daily_logs", [])

    log = next((dl for dl in daily_logs if dl.get("date") == date), None)
    if log is None:
        log = _new_daily_log(date, user)
        daily_logs.append(log)

    log.setdefault("workouts", [])
    key = workout.get("key")
    if key and any(w.get("key") == key for w in log["workouts"]):
        return serialize_user(user)  # đã ghi buổi này rồi -> bỏ qua (idempotent)

    log["workouts"].append(workout)
    log["calories_burned"] = round(
        sum((w.get("calories_burned") or 0) for w in log["workouts"]), 1
    )

    get_users_collection().update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"daily_logs": daily_logs}}
    )
    user["daily_logs"] = daily_logs
    return serialize_user(user)
