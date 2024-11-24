from datetime import datetime

from pydantic import BaseModel, Field


class OrderBase(BaseModel):
    instrument: str
    operation: str = Field(..., pattern="^[BS]$")
    price: float
    remaining_qty: int
    timestamp: datetime


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    remaining_qty: int = Field(..., ge=0)


class OrderResponse(OrderBase):
    id: int

    class Config:
        from_attributes = True
