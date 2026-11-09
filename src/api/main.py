"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.telemetry import setup_logging, logger
from src.core.database import engine
from src.models.base import Base
from src.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    setup_logging()
    logger.info(
        "starting_system",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT.value,
        autonomy_mode=settings.AUTONOMY_MODE.value,
    )
    # Ensure database schema is created (especially useful for sqlite/local dev)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_tables_verified")

    yield

    logger.info("shutting_down_system")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent multi-asset investment intelligence, risk management, and quantitative analysis platform.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    """System welcome and operational state."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "mode": settings.AUTONOMY_MODE.value,
        "docs_url": "/docs",
        "health_url": f"{settings.API_V1_STR}/health",
    }
