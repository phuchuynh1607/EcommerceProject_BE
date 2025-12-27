from sqlalchemy import Column, Integer,ForeignKey
from sqlalchemy.orm import relationship
from EcommerceApp.database import Base

class Carts(Base):
    __tablename__ ='carts'

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    product_id = Column(Integer,ForeignKey("products.id"))
    quantity=Column(Integer,default =1)

    product=relationship("Products")