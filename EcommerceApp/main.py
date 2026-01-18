from fastapi import FastAPI
from EcommerceApp.database import Base,engine
from EcommerceApp.routers import auth,admin,users,products,carts,orders
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Cấu hình danh sách các nguồn được phép (Origins)
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

Base.metadata.create_all(bind=engine)
@app.get("/")
def home():
    return {"status": "ok", "message": "Backend is running!"}

@app.get("/healthy")
def health_check():
    return {'status':'Healthy'}

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(carts.router)
app.include_router(orders.router)