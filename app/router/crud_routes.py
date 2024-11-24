from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import (
    add_order,
    delete_order,
    get_active_order_by_id,
    get_active_orders,
    update_order,
)
from app.database import async_session
from app.schemas import OrderCreate, OrderResponse, OrderUpdate

router = APIRouter()


async def get_db():
    async with async_session() as session:
        yield session


@router.post("/orders/", response_model=OrderResponse)
async def create_order(
    instrument: str,
    operation: str,
    price: float,
    remaining_qty: int,
    timestamp: datetime,
    db: AsyncSession = Depends(get_db),
):
    order_data = OrderCreate(
        instrument=instrument,
        operation=operation,
        price=price,
        remaining_qty=remaining_qty,
        timestamp=timestamp,
    )
    return await add_order(db, order_data)


@router.put("/orders/{order_id}", response_model=OrderResponse)
async def modify_order(
    order_id: int, update_data: OrderUpdate, db: AsyncSession = Depends(get_db)
):
    updated_order = await update_order(db, order_id, update_data)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order


@router.delete("/orders/{order_id}")
async def remove_order(order_id: int, db: AsyncSession = Depends(get_db)):
    await delete_order(db, order_id)
    return {"detail": "Order deleted"}


@router.get("/orders/", response_model=List[OrderResponse])
async def list_active_orders(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await get_active_orders(db, limit=limit, offset=offset)


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order_by_id(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await get_active_order_by_id(order_id, db)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
