from datetime import datetime
from enum import Enum
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class OrderStatus(str, Enum):
    NEW="new"; ACCEPTED="accepted"; COOKING="cooking"; DELIVERY="delivery"; COMPLETED="completed"; CANCELLED="cancelled"

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True)
    telegram_id: Mapped[int]=mapped_column(BigInteger,unique=True,index=True)
    username: Mapped[str|None]=mapped_column(String(255))
    first_name: Mapped[str|None]=mapped_column(String(255))
    phone: Mapped[str|None]=mapped_column(String(50))
    orders: Mapped[list["Order"]]=relationship(back_populates="user")

class Pizza(Base):
    __tablename__ = "pizzas"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    price_25: Mapped[int] = mapped_column(Integer)
    price_30: Mapped[int] = mapped_column(Integer)
    price_35: Mapped[int] = mapped_column(Integer)
    image_file_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="pizza"
    )

class Order(Base):
    __tablename__="orders"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id"))
    status: Mapped[str]=mapped_column(String(30),default=OrderStatus.NEW.value)
    customer_name: Mapped[str]=mapped_column(String(255))
    phone: Mapped[str]=mapped_column(String(50))
    address: Mapped[str]=mapped_column(Text)
    comment: Mapped[str|None]=mapped_column(Text)
    payment_method: Mapped[str]=mapped_column(String(50))
    subtotal: Mapped[int]=mapped_column(Integer)
    delivery_price: Mapped[int]=mapped_column(Integer)
    total: Mapped[int]=mapped_column(Integer)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,index=True)
    user: Mapped["User"]=relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]]=relationship(back_populates="order",cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__="order_items"
    id: Mapped[int]=mapped_column(primary_key=True)
    order_id: Mapped[int]=mapped_column(ForeignKey("orders.id"))
    pizza_id: Mapped[int]=mapped_column(ForeignKey("pizzas.id"))
    pizza_name: Mapped[str]=mapped_column(String(255))
    size: Mapped[int]=mapped_column(Integer)
    quantity: Mapped[int]=mapped_column(Integer)
    unit_price: Mapped[int]=mapped_column(Integer)
    order: Mapped["Order"]=relationship(back_populates="items")
    pizza: Mapped["Pizza"]=relationship(back_populates="items")
