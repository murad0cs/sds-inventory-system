from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from app.api import chemicals, audit
from app.db.base import engine
from app.core.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize logging on startup
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Application started - SDS Chemical Inventory System v1.1.0")
    yield
    logger.info("Application shutting down")
    await engine.dispose()


app = FastAPI(
    title="SDS Chemical Inventory System",
    description="A Safety Data Sheet (SDS) Chemical Inventory and Reporting System with Transaction Logging",
    version="1.1.0",
    lifespan=lifespan
)

app.include_router(chemicals.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "SDS Chemical Inventory System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}