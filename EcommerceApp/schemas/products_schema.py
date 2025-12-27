from pydantic import BaseModel, Field


class ProductRequest(BaseModel):
    title:str=Field(min_length=4)
    description:str=Field(min_length=3,max_length=50)
    price:float=Field(gt=0)
    stock:int=Field(gt=-1)