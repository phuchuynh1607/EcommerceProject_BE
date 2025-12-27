from pydantic import BaseModel, Field


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