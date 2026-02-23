import logging

from fastapi import FastAPI,Request
from EcommerceApp.database import Base,engine
from EcommerceApp.routers import auth,admin,users,products,carts,orders
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from EcommerceApp.config.env_config import settings
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


# Cấu hình logging cơ bản
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"--- Khởi động hệ thống: {settings.env} ---")

    try:
        # Chỉ tự động tạo bảng nếu là môi trường dev
        if settings.env == "development":
            Base.metadata.create_all(bind=engine)
            logger.info("Database: Đã kiểm tra và cập nhật cấu hình bảng (Dev Mode)")
        else:
            logger.info("Database: Bỏ qua tự động tạo bảng (Production Mode)")

    except Exception as e:
        logger.error("Database: Lỗi khởi tạo", exc_info=True)

    yield
    logger.info("--- Hệ thống đóng an toàn ---")

app = FastAPI(
title=settings.app_title,
    # Ẩn Swagger/ReDoc nếu đang ở production
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json"
    ,lifespan=lifespan
)
limiter = Limiter(key_func=get_remote_address,default_limits=["5/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount thư mục để có thể xem ảnh qua URL
app.mount("/static", StaticFiles(directory="static"), name="static")
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Cho phép các nguồn trong danh sách
    allow_credentials=True,
    allow_methods=["*"],              # Cho phép tất cả các phương thức (GET, POST,...)
    allow_headers=["*"],              # Cho phép tất cả các headers
)
app.add_middleware(SlowAPIMiddleware)


@app.get("/")
@limiter.limit("5/minute")
def home(request: Request):
    return {"status": "ok", "message": "Backend is running!"}

@app.get("/healthy")
@limiter.limit("5/minute")
def health_check(request: Request):
    return {'status':'Healthy'}

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(carts.router)
app.include_router(orders.router)