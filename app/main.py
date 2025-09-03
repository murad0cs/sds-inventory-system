from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import chemicals
from app.db.base import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="SDS Chemical Inventory System",
    description="A Safety Data Sheet (SDS) Chemical Inventory and Reporting System",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(chemicals.router, prefix="/api/v1")


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