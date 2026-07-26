"""Controller xác thực & hồ sơ người dùng (port từ Nutrition Warrior).

Giữ nguyên hình dạng response {success, message, data} như NW để frontend
SmartMeal dùng lại được. Các endpoint phụ thuộc dịch vụ ngoài của NW
(reset-password/OTP qua email, upload ảnh Cloudinary) tạm thời chưa port vì
SmartMeal chưa cấu hình các dịch vụ đó.
"""

from fastapi import APIRouter

from ..schemas.user import LoginIn, RegisterIn, UpdateHeightWeightIn, UpdateUserIn
from ..services import user as service
from ..services.user import UserError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("")
def register(data: RegisterIn):
    try:
        created = service.create_user(data.model_dump())
        return {"success": True, "message": "User created successfully", "data": created}
    except UserError as e:
        return {"success": False, "message": e.message}


@router.post("/login")
def login(data: LoginIn):
    try:
        user = service.login(data.email, data.password)
        return {"success": True, "message": "Login successful", "data": user}
    except UserError as e:
        return {"success": False, "message": e.message}


@router.get("/detail/{email}")
def user_info(email: str):
    try:
        user = service.get_user_info(email)
        return {"success": True, "data": user}
    except UserError as e:
        return {"success": False, "message": e.message}


@router.put("/update/{user_id}")
def update_user(user_id: str, data: UpdateUserIn):
    try:
        user = service.update_user(user_id, data.model_dump())
        return {"success": True, "message": "User update successful", "data": user}
    except UserError as e:
        return {"success": False, "message": e.message}


@router.put("/updatehw/{user_id}")
def update_height_weight(user_id: str, data: UpdateHeightWeightIn):
    try:
        result = service.update_height_weight(user_id, data.height, data.current_weight)
        return {"success": True, "message": "User update successful", "data": result}
    except UserError as e:
        return {"success": False, "message": e.message}
