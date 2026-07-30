"""Service cho nhật ký dinh dưỡng theo ngày (daily log).

Mỗi user có mảng `daily_logs`. Một log đại diện cho 1 ngày, gồm các bữa
breakfast/lunch/dinner và tổng hợp lượng nạp (intake) / còn lại (remain) so
với mục tiêu dinh dưỡng của user. Logic bám theo `add_food_to_daily_log` của
Nutrition Warrior.
"""

from bson import ObjectId

from ..core.database import get_users_collection
from .user import UserError, serialize_user, get_user_by_id

MEALS = ("breakfast", "lunch", "dinner")


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


def _recompute_totals(log: dict, user: dict) -> None:
    """Tính lại intake/remain của `log` từ chính các món đang có trong 3 bữa.

    Cộng dồn khi thêm rồi trừ dần khi xoá sẽ tích luỹ sai số dấu phẩy động và
    không tự sửa được nếu một lần ghi nào đó lệch; tính lại từ mảng món luôn
    cho ra con số khớp với những gì nhật ký đang hiển thị.
    """
    totals = {"ENERC_KCAL": 0.0, "PROCNT": 0.0, "CHOCDF": 0.0, "FAT": 0.0}
    for meal in MEALS:
        for item in log.get(meal) or []:
            nutrients = item.get("nutrients") or {}
            for key in totals:
                totals[key] += nutrients.get(key, 0) or 0

    log["caloric_intake"] = totals["ENERC_KCAL"]
    log["protein_intake"] = totals["PROCNT"]
    log["carb_intake"] = totals["CHOCDF"]
    log["fat_intake"] = totals["FAT"]

    # Lượng còn lại so với mục tiêu (không âm).
    log["caloric_remain"] = max(0.0, user.get("caloric_intake_goal", 0.0) - log["caloric_intake"])
    log["protein_remain"] = max(0.0, user.get("daily_protein_goal", 0.0) - log["protein_intake"])
    log["carb_remain"] = max(0.0, user.get("daily_carb_goal", 0.0) - log["carb_intake"])
    log["fat_remain"] = max(0.0, user.get("daily_fat_goal", 0.0) - log["fat_intake"])


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

    log.setdefault(meal, []).append(food_item)
    _recompute_totals(log, user)

    get_users_collection().update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"daily_logs": daily_logs}}
    )
    user["daily_logs"] = daily_logs
    return serialize_user(user)


def remove_food_from_daily_log(
    user_id: str, date: str, meal: str, index: int, label: str | None = None
) -> dict:
    """Xoá món thứ `index` khỏi bữa `meal` của ngày `date`, tính lại intake/remain.

    `index` là vị trí trong mảng bữa ăn - đúng thứ tự client đang hiển thị. Nếu
    client gửi kèm `label`, tên phải khớp với món ở vị trí đó thì mới xoá: danh
    sách có thể đã đổi (thêm món từ thiết bị khác) giữa lúc màn hình render và
    lúc bấm xoá, và xoá nhầm món thì không khôi phục lại được.
    Trả về user đã serialize, giống `add_food_to_daily_log`.
    """
    user = get_user_by_id(user_id)
    daily_logs = user.get("daily_logs", [])

    log = next((dl for dl in daily_logs if dl.get("date") == date), None)
    if log is None:
        raise UserError("Không tìm thấy nhật ký của ngày này", 404)

    items = log.get(meal) or []
    if index < 0 or index >= len(items):
        raise UserError("Món cần xoá không còn trong nhật ký", 404)

    if label is not None and (items[index].get("label") or "") != label:
        raise UserError(
            "Nhật ký đã thay đổi, hãy tải lại rồi xoá lại cho đúng món", 409
        )

    items.pop(index)
    log[meal] = items
    _recompute_totals(log, user)

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
