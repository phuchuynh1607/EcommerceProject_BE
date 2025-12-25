from .database import  Base
from sqlalchemy import Boolean,Column, Integer, String, ForeignKey,Float
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__='users'

    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True)
    username=Column(String,unique=True)
    first_name=Column(String)
    last_name=Column(String)
    hashed_password=Column(String)
    role=Column(String)
    phone_number=Column(String)
    is_active = Column(Boolean, default=True)



class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer,primary_key=True,index=True)
    title=Column(String)
    description=Column(String)
    price=Column(Float)
    stock=Column(Integer)

class Carts(Base):
    __tablename__ ='carts'

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    product_id = Column(Integer,ForeignKey("products.id"))
    quantity=Column(Integer,default =1)

    product=relationship("Products")

class Orders(Base):
    __tablename__='orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    total_price=Column(Float)
    status=Column(String,default="pending")


