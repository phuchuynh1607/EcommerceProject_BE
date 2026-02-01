from pydantic import BaseModel, Field,field_validator
from datetime import datetime
from typing import List

class ProductInOrder(BaseModel):
    title:str
    image: str | None = None  # Thêm dòng này để cho phép trả về ảnh

    class Config:
        from_attributes = True  # Đảm bảo Pydantic có thể đọc dữ liệu từ model SQLAlchemy

class OrderItemResponse(BaseModel):
    product_id:int=Field(gt=0)
    product:ProductInOrder
    quantity:int=Field(gt=0)
    price_at_purchase:float

    class Config:
        from_attributes=True

class OrderResponse(BaseModel):
    id:int=Field(gt=0)
    total_amount:float
    status:str
    created_at:datetime
    items:List[OrderItemResponse]

    class Config:
        from_attributes=True
class UpdateOrderStatus(BaseModel):
    status:str

    @field_validator('status')
    def validate_status(cls,v):
        allowed=['pending','completed','shipped','cancelled']
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v


