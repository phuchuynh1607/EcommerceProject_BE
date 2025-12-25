from fastapi import APIRouter,HTTPException,Path
from pydantic import BaseModel,Field
from ..models import Products
from starlette import status
from .auth import user_dependency,db_dependency

router=APIRouter(prefix='/products',tags=['products'])


class ProductRequest(BaseModel):
    title:str=Field(min_length=4)
    description:str=Field(min_length=3,max_length=50)
    price:float=Field(gt=0)
    stock:int=Field(gt=-1)

@router.get("/",status_code=status.HTTP_200_OK)
async def read_all_products(db:db_dependency):
    return db.query(Products).all()

@router.get("/product/{product_id}",status_code=status.HTTP_200_OK)
async def read_product(db:db_dependency,product_id:int =Path(gt=0)):
    product=db.query(Products).filter(Products.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404,detail="Can't find product!")
    return product

@router.post("/product",status_code=status.HTTP_201_CREATED)
async def create_product(user:user_dependency
                         ,db:db_dependency
                         ,product_request:ProductRequest):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')

    product_model=Products(**product_request.model_dump())

    db.add(product_model)
    db.commit()
    db.refresh(product_model)
    return product_model

@router.put("/product/{product_id}",status_code=status.HTTP_200_OK)
async def update_product(user:user_dependency,
                         db:db_dependency
                         ,product_request:ProductRequest
                         ,product_id:int=Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')

    product_model=db.query(Products).filter(Products.id == product_id).first()

    if product_model is None:
        raise HTTPException(status_code=404, detail="Can't find product!")

    product_model.title=product_request.title
    product_model.description=product_request.description
    product_model.price=product_request.price
    product_model.stock=product_request.stock

    db.add(product_model)
    db.commit()
    db.refresh(product_model)
    return product_model

@router.delete("/product/{product_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(user:user_dependency
                         ,db:db_dependency
                         ,product_id:int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')

    product_model=db.query(Products).filter(Products.id == product_id).first()

    if product_model is None:
        raise HTTPException(status_code=404, detail="Can't find product!")

    db.delete(product_model)
    db.commit()
