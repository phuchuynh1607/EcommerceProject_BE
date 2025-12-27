from datetime import datetime
from sqlalchemy import DateTime
from EcommerceApp.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey,Float
from sqlalchemy.orm import relationship

class Orders(Base):
    __tablename__='orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    total_amount=Column(Float)
    status=Column(String,default="pending") #pending,completed,shipped,cancelled
    created_at=Column(DateTime,default=datetime.now)

    user=relationship("Users",back_populates="orders")
    items=relationship("OrderItems",back_populates="order",cascade="all, delete-orphan")

class OrderItems(Base):
    __tablename__='order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id= Column(Integer,ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    price_at_purchase=Column(Float)
    quantity = Column(Integer, default=1)

    order=relationship("Orders",back_populates="items")
    product = relationship("Products")