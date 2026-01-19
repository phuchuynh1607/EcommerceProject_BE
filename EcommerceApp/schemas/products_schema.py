from typing import Optional
from pydantic import BaseModel, Field

class ProductRequest(BaseModel):
    category: str=Field(min_length=3)
    title: str = Field(min_length=3)
    description: str = Field(min_length=10)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    rating: float = Field(default=0.0, ge=0, le=5) # Thêm trường này
    review_count: int = Field(default=0, ge=0)   # Thêm trường này
    image_url: Optional[str] = None
