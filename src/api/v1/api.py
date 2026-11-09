"""API v1 router aggregator."""

from fastapi import APIRouter
from src.api.v1.endpoints import health, assets, portfolio, signals, risk

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(assets.router)
api_router.include_router(portfolio.router)
api_router.include_router(signals.router)
api_router.include_router(risk.router)
