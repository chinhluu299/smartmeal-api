from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import close_client, ensure_indexes
from .controllers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tạo index (vd email unique) nếu MongoDB sẵn sàng; lỗi kết nối không
    # được chặn app khởi động (kết nối là lazy).
    try:
        ensure_indexes()
    except Exception:
        pass
    yield
    close_client()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    return app


app = create_app()
