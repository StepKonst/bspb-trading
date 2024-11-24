import csv
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import ActiveOrder
from app.schemas import OrderCreate, OrderUpdate


def detect_delimiter(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        sample = file.readline()
        if ";" in sample:
            return ";"
        elif "," in sample:
            return ","
        else:
            raise ValueError("Не удалось определить разделитель. Проверьте файл.")


async def load_csv_to_db(session: AsyncSession, csv_path: str, chunk_size: int = 10000):
    delimiter = detect_delimiter(csv_path)
    orders = {}

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        for row in reader:
            action = int(row["ACTION"])
            order_id = row["ID"]

            if action == 1:
                orders[order_id] = {
                    "instrument": row["SYMBOL"],
                    "operation": row["TYPE"],
                    "price": Decimal(row["PRICE"]).quantize(Decimal("0.01")),
                    "remaining_qty": int(row["VOLUME"]),
                    "timestamp": datetime.strptime(row["MOMENT"], "%Y%m%d%H%M%S%f"),
                }
            elif action == 0 and order_id in orders:
                del orders[order_id]
            elif action == 2 and order_id in orders:
                executed_qty = int(row["VOLUME"])
                orders[order_id]["remaining_qty"] -= executed_qty

                if orders[order_id]["remaining_qty"] <= 0:
                    del orders[order_id]

    batch = [
        ActiveOrder(
            instrument=order["instrument"],
            operation=order["operation"],
            price=order["price"],
            remaining_qty=order["remaining_qty"],
            timestamp=order["timestamp"],
        )
        for order in orders.values()
    ]

    for i in range(0, len(batch), chunk_size):
        session.add_all(batch[i : i + chunk_size])
        await session.commit()


async def get_active_order_price(
    instrument: str, timestamp: datetime, session: AsyncSession
):
    highest_buy_price_query = (
        select(func.max(ActiveOrder.price))
        .filter(
            ActiveOrder.instrument == instrument,
            ActiveOrder.timestamp <= timestamp,
            ActiveOrder.remaining_qty > 0,
            ActiveOrder.operation == "B",
        )
        .scalar_subquery()
    )

    lowest_sell_price_query = (
        select(func.min(ActiveOrder.price))
        .filter(
            ActiveOrder.instrument == instrument,
            ActiveOrder.timestamp <= timestamp,
            ActiveOrder.remaining_qty > 0,
            ActiveOrder.operation == "S",
        )
        .scalar_subquery()
    )

    query = select(
        highest_buy_price_query.label("highest_buy_price"),
        lowest_sell_price_query.label("lowest_sell_price"),
    )

    result = await session.execute(query)
    data = result.fetchone()

    if data is not None:
        return {"highest_buy_price": data[0], "lowest_sell_price": data[1]}
    return None


async def add_order(session: AsyncSession, order_data: OrderCreate):
    order = ActiveOrder(**order_data.dict())
    session.add(order)
    await session.commit()
    return order


async def update_order(session: AsyncSession, order_id: int, update_data: OrderUpdate):
    query = select(ActiveOrder).where(ActiveOrder.id == order_id)
    result = await session.execute(query)
    try:
        order = result.scalar_one()
        order.remaining_qty = update_data.remaining_qty
        if update_data.remaining_qty == 0:
            await session.delete(order)
        await session.commit()
        return order
    except NoResultFound:
        return None


async def delete_order(session: AsyncSession, order_id: int):
    query = select(ActiveOrder).where(ActiveOrder.id == order_id)
    result = await session.execute(query)
    try:
        order = result.scalar_one()
        await session.delete(order)
        await session.commit()
    except NoResultFound:
        return None


async def get_active_orders(session: AsyncSession, limit: int = 10, offset: int = 0):
    query = select(ActiveOrder).offset(offset).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


async def get_active_order_by_id(order_id: int, session: AsyncSession):
    query = select(ActiveOrder).filter(ActiveOrder.id == order_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()
