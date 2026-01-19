from sqlalchemy import Column, Integer, String, Float

from EcommerceApp.database import Base
class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer,primary_key=True,index=True)
    category = Column(String,nullable=True)
    title=Column(String)
    description=Column(String)
    price=Column(Float)
    stock=Column(Integer)
    rating=Column(Float,default=0.0)
    review_count=Column(Integer,default=0)
    image_url = Column(String, nullable=True)