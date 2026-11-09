"""Application configuration using Pydantic Settings."""

from enum import Enum
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AutonomyMode(str, Enum):
    """Progressive autonomy stages for the investment system."""
    ANALYST_ONLY = "ANALYST_ONLY"           # Stage 1: Read-only, simulations, signals
    PAPER_TRADING = "PAPER_TRADING"         # Stage 2: Simulated live trading without real money
    SUPERVISED = "SUPERVISED"               # Stage 3: Real execution ONLY after human 2FA approval
    LIMITED_AUTONOMY = "LIMITED_AUTONOMY"   # Stage 4: Strict bounded autonomous execution


class Environment(str, Enum):
    """Runtime environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """System-wide configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # General
    PROJECT_NAME: str = "AI Investment Intelligence"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    AUTONOMY_MODE: AutonomyMode = AutonomyMode.ANALYST_ONLY
    ALLOWED_HOSTS: List[str] = ["*"]
    SECRET_KEY: str = "default_development_secret_key_change_me_in_production"

    # Investor Capital Scenario (Base reference for simulations)
    INITIAL_CAPITAL_EUR: float = Field(default=20000.00, ge=1000.0)
    ALLOCATION_LONG_TERM_PCT: float = Field(default=0.50, ge=0.0, le=1.0)
    ALLOCATION_TACTICAL_PCT: float = Field(default=0.15, ge=0.0, le=1.0)
    ALLOCATION_CRYPTO_PCT: float = Field(default=0.10, ge=0.0, le=1.0)
    ALLOCATION_LIQUIDITY_PCT: float = Field(default=0.25, ge=0.0, le=1.0)

    # Central Sovereign Risk Engine Limits
    RISK_MAX_PER_TRADE_PCT: float = Field(default=0.0050, ge=0.001, le=0.02)  # 0.50% max
    RISK_MAX_AGGREGATE_PCT: float = Field(default=0.0150, ge=0.005, le=0.05)  # 1.50% max
    RISK_MAX_DAILY_LOSS_PCT: float = Field(default=0.0100, ge=0.005, le=0.03) # 1.00% max
    RISK_MAX_WEEKLY_LOSS_PCT: float = Field(default=0.0200, ge=0.01, le=0.05) # 2.00% max
    RISK_DRAWDOWN_REVIEW_PCT: float = Field(default=0.0800, ge=0.03, le=0.15) # 8.00% review
    RISK_DRAWDOWN_HALT_PCT: float = Field(default=0.1000, ge=0.05, le=0.20)   # 10.00% stop
    LEVERAGE_ALLOWED: bool = False  # Strictly False for Phase 1

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./investment_intelligence.db"

    # Redis Cache
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # External APIs (Optional in Phase 1)
    FRED_API_KEY: str = ""
    FMP_API_KEY: str = ""

    @field_validator("ALLOCATION_LIQUIDITY_PCT")
    @classmethod
    def validate_allocations_sum(cls, v: float, info) -> float:
        """Validate that target portfolio bucket allocations sum to approximately 1.0."""
        data = info.data
        lt = data.get("ALLOCATION_LONG_TERM_PCT", 0.50)
        tc = data.get("ALLOCATION_TACTICAL_PCT", 0.15)
        cr = data.get("ALLOCATION_CRYPTO_PCT", 0.10)
        total = lt + tc + cr + v
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Portfolio allocations must sum to 1.0 (currently {total})")
        return v


settings = Settings()
