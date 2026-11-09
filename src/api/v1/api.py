"""API v1 router aggregator."""

from fastapi import APIRouter
from src.api.v1.endpoints import health, assets, portfolio, signals, risk, market_data

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(assets.router)
api_router.include_router(portfolio.router)
api_router.include_router(signals.router)
api_router.include_router(risk.router)
api_router.include_router(market_data.router)
