from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, Literal
from datetime import datetime

OrderStatusType = Literal['pending', 'confirmed', 'cancelled']


class UserRegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserOutputSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    registered_date: datetime


class UserShortSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class ProductInputSchema(BaseModel):
    product_name: str
    price: float = Field(gt=0)
    description: Optional[str] = None


class ProductUpdateSchema(BaseModel):
    product_name: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    description: Optional[str] = None


class ProductOutputSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_name: str
    price: float
    description: Optional[str] = None
    created_date: datetime


class OrderInputSchema(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class OrderUpdateSchema(BaseModel):
    quantity: Optional[int] = Field(default=None, ge=1)
    order_status: Optional[OrderStatusType] = None


class OrderOutputSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    order_status: str
    created_date: datetime