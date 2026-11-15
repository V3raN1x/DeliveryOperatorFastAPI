from datetime import datetime
from typing import List
from sqlalchemy import Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base



class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    registered_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_token: Mapped[List['RefreshToken']] = relationship(
        'RefreshToken', back_populates='token_user', cascade='all, delete-orphan')
    orders: Mapped[List['Order']] = relationship(
        'Order', back_populates='user', cascade='all, delete-orphan')

    def __str__(self):
        return self.username


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    token_user: Mapped[User] = relationship(User, back_populates='user_token')
    token: Mapped[str] = mapped_column(String)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    orders: Mapped[List['Order']] = relationship(
        'Order', back_populates='product', cascade='all, delete-orphan')

    def __str__(self):
        return self.product_name


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped[User] = relationship(User, back_populates='orders')
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped[Product] = relationship(Product, back_populates='orders')
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    total_price: Mapped[float] = mapped_column(Float)
    order_status: Mapped[str] = mapped_column(String(20), default='pending')
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)