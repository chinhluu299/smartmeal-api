"""Service cho module tập luyện.

- Các danh sách tĩnh (body part / equipment / target) trả về trực tiếp.
- Dữ liệu bài tập được CACHE trong MongoDB: lần đầu tự đồng bộ từ ExerciseDB
  (RapidAPI, có giới hạn request/tháng) rồi sau đó phục vụ hoàn toàn từ DB.
  Nếu MongoDB lỗi/chưa cấu hình, tự động fallback gọi thẳng ExerciseDB.
"""

import re

import requests
from bson.binary import Binary

from ..core.config import settings
from ..core.database import (
    ensure_indexes,
    get_exercise_images_collection,
    get_exercises_collection,
)

BODY_PARTS = [
    "back", "cardio", "chest", "lower arms", "lower legs",
    "neck", "shoulders", "upper arms", "upper legs", "waist",
]

EQUIPMENT_LIST = [
    "assisted", "band", "barbell", "body weight", "bosu ball",
    "cable", "dumbbell", "elliptical machine", "ez barbell", "hammer",
    "kettlebell", "leverage machine", "medicine ball", "olympic barbell",
    "resistance band", "roller", "rope", "skierg machine", "sled machine",
    "smith machine", "stability ball", "stationary bike", "stepmill machine",
    "tire", "trap bar", "upper body ergometer", "weighted", "wheel roller",
]

TARGET_LIST = [
    "abductors", "abs", "adductors", "biceps", "calves",
    "cardiovascular system", "delts", "forearms", "glutes",
    "hamstrings", "lats", "levator scapulae", "pectorals",
    "quads", "serratus anterior", "spine", "traps", "triceps",
    "upper back",
]


# ---------------------------------------------------------------------------
# Gọi trực tiếp ExerciseDB (RapidAPI) - chỉ dùng để đồng bộ DB hoặc fallback
# ---------------------------------------------------------------------------
def _fetch(path: str, limit: str = "10", offset: int | None = None):
    """Gọi ExerciseDB và trả về JSON. Ném requests.RequestException nếu lỗi.

    Lưu ý: gói RapidAPI hiện tại chặn `limit` ở mức tối đa 10 bản ghi/lần gọi,
    nên muốn lấy hết phải phân trang bằng `offset`.
    """
    params: dict = {"limit": limit}
    if offset is not None:
        params["offset"] = offset
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
    }
    response = requests.get(
        f"{settings.EXERCISEDB_BASE_URL}{path}",
        params=params,
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Đồng bộ & truy vấn từ MongoDB
# ---------------------------------------------------------------------------
def _to_int(limit, default: int = 10) -> int:
    try:
        return int(limit)
    except (TypeError, ValueError):
        return default


def _clean(doc: dict) -> dict:
    """Bỏ `_id` nội bộ của Mongo (giữ lại field `id` gốc của ExerciseDB)."""
    doc.pop("_id", None)
    return doc


_PAGE_SIZE = 10  # RapidAPI chặn limit tối đa 10/lần gọi


def sync_exercises_to_db(start_offset: int = 0, max_pages: int | None = None) -> dict:
    """Phân trang tải bài tập từ ExerciseDB và upsert vào MongoDB.

    - Idempotent: chạy lại sẽ cập nhật, không tạo trùng (key theo `id`).
    - Resumable: nếu gọi API lỗi giữa chừng (vd hết quota), hàm dừng và trả về
      `next_offset` để bạn gọi lại với `start_offset=next_offset`.

    Trả về dict gồm: synced, pages, next_offset, total_in_db, (error nếu có).
    """
    ensure_indexes()
    col = get_exercises_collection()
    offset = start_offset
    synced = 0
    pages = 0
    error = None

    while max_pages is None or pages < max_pages:
        try:
            page = _fetch("/exercises", limit=str(_PAGE_SIZE), offset=offset)
        except requests.RequestException as e:
            error = f"Dừng tại offset {offset}: {e}"
            break
        if not isinstance(page, list) or not page:
            break
        for ex in page:
            ex_id = ex.get("id")
            if not ex_id:
                continue
            col.replace_one({"_id": ex_id}, {**ex, "_id": ex_id}, upsert=True)
            synced += 1
        pages += 1
        offset += len(page)
        if len(page) < _PAGE_SIZE:  # trang cuối
            break

    result = {
        "synced": synced,
        "pages": pages,
        "next_offset": offset,
        "total_in_db": db_count(),
    }
    if error:
        result["error"] = error
    return result


def db_count() -> int:
    return get_exercises_collection().estimated_document_count()


def _query_db(filt: dict, limit) -> list:
    """Truy vấn cache. Ném RuntimeError nếu cache rỗng để caller fallback API."""
    if db_count() == 0:
        raise RuntimeError("Exercise cache rỗng - hãy gọi POST /exercises/sync")
    n = _to_int(limit)
    cursor = get_exercises_collection().find(filt)
    if n > 0:
        cursor = cursor.limit(n)
    return [_clean(d) for d in cursor]


def _ci_exact(value: str) -> dict:
    """Khớp chính xác, không phân biệt hoa thường."""
    return {"$regex": f"^{re.escape(value)}$", "$options": "i"}


# ---------------------------------------------------------------------------
# API public (controller gọi). Ưu tiên DB, lỗi DB -> fallback ExerciseDB.
# ---------------------------------------------------------------------------
def get_all_exercises(limit: str = "10"):
    try:
        return _query_db({}, limit)
    except Exception:
        return _fetch("/exercises", limit)


def get_exercises_by_name(name: str, limit: str = "10"):
    try:
        filt = {"name": {"$regex": re.escape(name), "$options": "i"}}
        return _query_db(filt, limit)
    except Exception:
        return _fetch(f"/exercises/name/{name}", limit)


def get_exercises_by_body_part(body_part: str, limit: str = "20"):
    try:
        return _query_db({"bodyPart": _ci_exact(body_part)}, limit)
    except Exception:
        return _fetch(f"/exercises/bodyPart/{body_part}", limit)


def get_exercises_by_equipment(equipment: str, limit: str = "20"):
    try:
        return _query_db({"equipment": _ci_exact(equipment)}, limit)
    except Exception:
        return _fetch(f"/exercises/equipment/{equipment}", limit)


def get_exercises_by_target(target: str, limit: str = "10"):
    try:
        return _query_db({"target": _ci_exact(target)}, limit)
    except Exception:
        return _fetch(f"/exercises/target/{target}", limit)


def _fetch_image_remote(exercise_id: str, resolution: str = "360"):
    """Tải ảnh động (gif) trực tiếp từ ExerciseDB.

    ExerciseDB mới không còn trả `gifUrl` trong JSON; ảnh phục vụ qua endpoint
    riêng và yêu cầu API key ở header nên app không gọi trực tiếp được.
    Trả về (bytes, content_type).
    """
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
    }
    response = requests.get(
        f"{settings.EXERCISEDB_BASE_URL}/image",
        params={"exerciseId": exercise_id, "resolution": resolution},
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    return response.content, response.headers.get("content-type", "image/gif")


def get_exercise_image(exercise_id: str, resolution: str = "360"):
    """Trả về ảnh GIF của bài tập, ưu tiên cache trong MongoDB.

    Lần đầu mỗi ảnh sẽ gọi ExerciseDB rồi lưu binary vào DB; các lần sau phục
    vụ thẳng từ DB (không tốn quota RapidAPI). Lỗi DB không ảnh hưởng response.
    """
    key = f"{exercise_id}_{resolution}"

    # 1) Thử lấy từ cache
    try:
        col = get_exercise_images_collection()
        cached = col.find_one({"_id": key})
        if cached and cached.get("data"):
            return bytes(cached["data"]), cached.get("content_type", "image/gif")
        # Đúng resolution chưa có, nhưng ảnh của bài tập này đã cache ở resolution
        # khác -> dùng luôn (cùng 1 GIF, app tự co giãn) để KHỎI gọi lại RapidAPI.
        # Nhờ vậy danh sách xin res=180 vẫn dùng được ảnh res=360 đã cache.
        alt = col.find_one({"exerciseId": exercise_id})
        if alt and alt.get("data"):
            return bytes(alt["data"]), alt.get("content_type", "image/gif")
    except Exception:
        pass  # DB lỗi -> tải thẳng từ remote

    # 2) Tải từ ExerciseDB
    content, content_type = _fetch_image_remote(exercise_id, resolution)

    # 3) Lưu cache (best-effort)
    _store_image(key, exercise_id, resolution, content, content_type)
    return content, content_type


def _store_image(key, exercise_id, resolution, content, content_type) -> bool:
    try:
        get_exercise_images_collection().replace_one(
            {"_id": key},
            {
                "_id": key,
                "exerciseId": exercise_id,
                "resolution": resolution,
                "content_type": content_type,
                "data": Binary(content),
            },
            upsert=True,
        )
        return True
    except Exception:
        return False


def images_count() -> int:
    return get_exercise_images_collection().estimated_document_count()


def sync_images_to_db(resolution: str = "360", start: int = 0,
                      limit: int | None = None) -> dict:
    """Tải trước ảnh GIF cho các bài tập đang có trong DB và lưu vào MongoDB.

    Mỗi ảnh là 1 lần gọi RapidAPI, nên với ~1300 bài tập sẽ tốn quota. Hàm bỏ
    qua ảnh đã cache (an toàn khi chạy lại), và resumable qua `start`/`limit`:
    nếu lỗi giữa chừng sẽ trả về `next_start` để chạy tiếp.
    """
    ids = [d["_id"] for d in get_exercises_collection()
           .find({}, {"_id": 1}).sort("_id", 1)]
    ids = ids[start:]
    if limit is not None:
        ids = ids[:limit]

    img_col = get_exercise_images_collection()
    cached = skipped = processed = 0
    error = None

    for ex_id in ids:
        key = f"{ex_id}_{resolution}"
        if img_col.find_one({"_id": key}, {"_id": 1}):
            skipped += 1
            processed += 1
            continue
        try:
            content, content_type = _fetch_image_remote(ex_id, resolution)
        except requests.RequestException as e:
            error = f"Dừng tại id {ex_id}: {e}"
            break
        _store_image(key, ex_id, resolution, content, content_type)
        cached += 1
        processed += 1

    result = {
        "cached": cached,
        "skipped": skipped,
        "processed": processed,
        "next_start": start + processed,
        "images_in_db": images_count(),
    }
    if error:
        result["error"] = error
    return result
