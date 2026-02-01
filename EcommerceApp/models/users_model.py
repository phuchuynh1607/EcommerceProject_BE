from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from EcommerceApp.database import Base


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
    gender = Column(String,nullable=True)
    user_image=Column(String,nullable=True)
    orders=relationship("Orders",back_populates="user")