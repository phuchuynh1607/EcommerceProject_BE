from fastapi import APIRouter,HTTPException,Path
from pydantic import BaseModel,Field
from ..models import Carts,Products
from .auth import user_dependency,db_dependency
from starlette import status



router=APIRouter(prefix='/carts',tags=['carts'])

class CartRequest(BaseModel):
    product_id:int = Field(gt=0)
    quantity:int=Field(gt=0)

class  ProductInCart(BaseModel):
    title:str
    price:float

class CartResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    user_id: int
    product: ProductInCart

    class Config:
        from_attributes = True

class CartUpdateRequest(BaseModel):
    quantity:int=Field(gt=0)

@router.get("/admin/all",status_code=status.HTTP_200_OK,response_model=list[CartResponse])
async def get_all_carts_admin(user:user_dependency,db:db_dependency):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=401,detail='Authentication Failed.')
    return db.query(Carts).all()

@router.get("/",status_code=status.HTTP_200_OK,response_model=list[CartResponse])
async def get_all_from_cart(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed.')
    return db.query(Carts).filter(Carts.user_id == user.get('id')).all()

@router.post("/cart",status_code=status.HTTP_201_CREATED)
async def add_to_cart(user:user_dependency
                      ,db:db_dependency
                      ,cart_request:CartRequest):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed.')

    product=db.query(Products).filter(Products.id == cart_request.product_id).first()
    if not product:
        raise HTTPException(status_code=404,detail='Product not found.')
    if product.stock == 0:
        raise HTTPException(status_code=400,detail='Sold out.')

    cart_model=db.query(Carts).filter(
        Carts.user_id == user.get('id'),
        Carts.product_id == cart_request.product_id,
    ).first()

    current_in_cart=cart_model.quantity if cart_model else 0
    total_request = current_in_cart + cart_request.quantity

    if product.stock < total_request:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. You can only add {product.stock - current_in_cart} more."
        )

    if cart_model:
        cart_model.quantity=total_request
    else:
        cart_model=Carts(
            **cart_request.model_dump(),
            user_id=user.get('id')
        )

    db.add(cart_model)
    db.commit()
    db.refresh(cart_model)
    return cart_model

@router.put("/quantity/{cart_id}",status_code=status.HTTP_200_OK,response_model=CartResponse)
async def update_cart(user:user_dependency,
                      db:db_dependency,
                      cart_request:CartUpdateRequest,
                      cart_id:int= Path(gt =0)):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed.')

    cart_model = db.query(Carts).filter(Carts.id == cart_id)\
    .filter(Carts.user_id == user.get('id')).first()

    if cart_model is None:
        raise HTTPException(status_code=404,detail='Product not found in your cart.')

    product=db.query(Products).filter(Products.id == cart_model.product_id).first()

    if not product:
        raise HTTPException(status_code=404,detail='Product no longer exists.')

    if product.stock < cart_request.quantity:
        raise HTTPException(status_code=400,
                            detail='Insufficient stock.')

    cart_model.quantity = cart_request.quantity
    db.add(cart_model)
    db.commit()
    db.refresh(cart_model)
    return cart_model

@router.delete("/delete/{cart_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_from_cart(user:user_dependency,
                                db:db_dependency
                                ,cart_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed.')

    cart_model = db.query(Carts).filter(Carts.id == cart_id)\
    .filter(Carts.user_id == user.get('id')).first()

    if cart_model is None:
        raise HTTPException(status_code=404, detail='Product not found in your cart.')

    db.query(Carts).filter(Carts.id == cart_id).delete()
    db.commit()
