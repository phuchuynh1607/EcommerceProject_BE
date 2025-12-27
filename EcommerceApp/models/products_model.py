from sqlalchemy import Column, Integer, String, Float

from EcommerceApp.database import Base
class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer,primary_key=True,index=True)
    title=Column(String)
    description=Column(String)
    price=Column(Float)
    stock=Column(Integer)