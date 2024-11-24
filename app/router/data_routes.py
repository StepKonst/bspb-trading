from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import get_active_order_price, load_csv_to_db
from app.database import async_session

router = APIRouter()


async def get_db():
    async with async_session() as session:
        yield session


@router.post("/load-csv/")
async def upload_csv(file: UploadFile, db: AsyncSession = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invalid file format. Only CSV files are allowed."
        )

    temp_file_path = f"/tmp/{file.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await file.read())

    await load_csv_to_db(db, temp_file_path)
    return {"detail": "Data successfully loaded into the database."}


@router.get("/active_orders/price_info")
async def get_active_order_price_info(
    instrument: str, timestamp: datetime, session: AsyncSession = Depends(get_db)
):
    """
    Возвращает самую высокую цену покупки и самую низкую цену продажи для указанного инструмента и времени.
    """
    data = await get_active_order_price(instrument, timestamp, session)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="No active orders found for the given instrument and time",
        )

    highest_buy_price = data["highest_buy_price"]
    lowest_sell_price = data["lowest_sell_price"]

    return {
        "highest_buy_price": highest_buy_price,
        "lowest_sell_price": lowest_sell_price,
    }
