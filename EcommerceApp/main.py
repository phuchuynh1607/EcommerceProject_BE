from fastapi import FastAPI
from EcommerceApp.database import Base,engine
from EcommerceApp.routers import auth,admin,users,products,carts,orders

app =FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/healthy")
def health_check():
    return {'status':'Healthy'}

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(carts.router)
app.include_router(orders.router)