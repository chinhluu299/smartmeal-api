import requests
from fastapi import APIRouter, HTTPException, Response

from ..services import exercise as service

router = APIRouter(prefix="/exercises", tags=["exercises"])


def _proxy(fetch_fn, *args):
    """Bọc lời gọi ExerciseDB trong envelope {success, data} giống NW."""
    try:
        data = fetch_fn(*args)
        return {"success": True, "data": data}
    except requests.RequestException as e:
        return {"success": False, "message": f"Request error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ----- Đồng bộ / trạng thái cache MongoDB -----
@router.post("/sync")
def sync_exercises(start: int = 0, max_pages: int | None = None):
    """Tải bài tập từ ExerciseDB về MongoDB (phân trang, chạy 1 lần để nạp cache).

    - `start`: offset bắt đầu (dùng để chạy tiếp nếu lần trước bị ngắt giữa chừng).
    - `max_pages`: giới hạn số trang mỗi lần gọi (mỗi trang 10 bài).
    """
    try:
        result = service.sync_exercises_to_db(start_offset=start, max_pages=max_pages)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/sync-images")
def sync_images(resolution: str = "360", start: int = 0, max: int | None = None):
    """Tải trước ảnh GIF của các bài tập trong DB và lưu vào MongoDB.

    Tốn nhiều quota (mỗi ảnh 1 request). Có thể chạy theo lô bằng `start`/`max`.
    Ảnh đã cache sẽ được bỏ qua. (Ảnh cũng tự cache khi user xem lần đầu.)
    """
    try:
        result = service.sync_images_to_db(resolution=resolution, start=start, limit=max)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/cache-status")
def cache_status():
    """Số bài tập và ảnh hiện có trong MongoDB."""
    try:
        return {
            "success": True,
            "data": {
                "exercises": service.db_count(),
                "images": service.images_count(),
            },
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


# ----- Danh sách tĩnh -----
@router.get("/get-body-part-list")
def get_body_part_list():
    return {"success": True, "data": service.BODY_PARTS}


@router.get("/get-equipment-list")
def get_equipment_list():
    return {"success": True, "data": service.EQUIPMENT_LIST}


@router.get("/get-target-list")
def get_target_list():
    return {"success": True, "data": service.TARGET_LIST}


# ----- Proxy ExerciseDB -----
@router.get("/get-all-exercises")
def get_all_exercises(limit: str = "10"):
    return _proxy(service.get_all_exercises, limit)


@router.get("/get-exercises-by-name/{name}")
def get_exercises_by_name(name: str, limit: str = "10"):
    return _proxy(service.get_exercises_by_name, name, limit)


@router.get("/get-exercises-for-body-part/{body_part}")
def get_exercises_for_body_part(body_part: str, limit: str = "20"):
    return _proxy(service.get_exercises_by_body_part, body_part, limit)


@router.get("/get-exercises-by-equipment/{equipment}")
def get_exercises_by_equipment(equipment: str, limit: str = "20"):
    return _proxy(service.get_exercises_by_equipment, equipment, limit)


@router.get("/get-exercises-by-target/{target}")
def get_exercises_by_target(target: str, limit: str = "10"):
    return _proxy(service.get_exercises_by_target, target, limit)


# ----- Proxy ảnh động (gif) của bài tập -----
@router.get("/image/{exercise_id}")
def get_exercise_image(exercise_id: str, resolution: str = "360"):
    try:
        content, content_type = service.get_exercise_image(exercise_id, resolution)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Image request error: {str(e)}")
    return Response(
        content=content,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )
