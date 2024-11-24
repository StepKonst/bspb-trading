import datetime

from sqlalchemy import TIMESTAMP, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base, engine


class ActiveOrder(Base):
    __tablename__ = "active_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    instrument: Mapped[str] = mapped_column(String, nullable=False)
    operation: Mapped[str] = mapped_column(String(1), nullable=False)
    price: Mapped[float] = mapped_column(Numeric, nullable=False)
    remaining_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
