from typing import Optional
from pydantic import BaseModel, Field

class ProductRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=4)
    description: Optional[str] = Field(default=None, min_length=3)
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = None