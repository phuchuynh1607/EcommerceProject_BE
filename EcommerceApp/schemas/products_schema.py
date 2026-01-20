from typing import Optional

from pydantic import BaseModel


class RatingRequest(BaseModel):
    rate: float
    count: int

class ProductRequest(BaseModel):
    title: str
    price: float
    description: str
    category: str
    image: str
    rating: RatingRequest
    stock: Optional[int] = 100