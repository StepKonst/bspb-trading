import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.models import init_db
from app.router.crud_routes import router as crud_operations
from app.router.data_routes import router as data_operations

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    await init_db()
    yield
    logger.info("Application shutdown")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI app. Visit /docs for API documentation."}


app.include_router(data_operations, prefix="/api", tags=["data"])
app.include_router(crud_operations, prefix="/api", tags=["orders"])
