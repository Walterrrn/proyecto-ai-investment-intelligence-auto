"""Portfolio management and allocation service."""

from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.config import settings
from src.models.asset import Asset, AllocationBucket
from src.models.portfolio import PortfolioPosition


class PortfolioService:
    """Service to compute portfolio metrics and allocation alignment."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_allocation_breakdown(self) -> Dict[str, Any]:
        """
        Calculate the current equity across the 4 asset buckets
        and compare with the reference simulation scenario.
        """
        stmt = select(PortfolioPosition).join(Asset)
        result = await self.session.execute(stmt)
        positions: List[PortfolioPosition] = list(result.scalars().all())

        buckets = {
            AllocationBucket.LONG_TERM.value: 0.0,
            AllocationBucket.TACTICAL.value: 0.0,
            AllocationBucket.CRYPTO.value: 0.0,
            AllocationBucket.LIQUIDITY.value: 0.0,
        }

        invested_total = 0.0
        for pos in positions:
            mkt_val = pos.market_value_eur
            invested_total += mkt_val
            bucket = pos.allocation_bucket
            if bucket in buckets:
                buckets[bucket] += mkt_val

        # Total capital includes free liquidity
        # If no positions are recorded yet, we simulate the configured scenario
        total_wealth = max(settings.INITIAL_CAPITAL_EUR, invested_total)
        liquidity = max(0.0, total_wealth - invested_total)
        buckets[AllocationBucket.LIQUIDITY.value] += liquidity

        # Compute percentages
        percentages = {
            bucket: (val / total_wealth) if total_wealth > 0 else 0.0
            for bucket, val in buckets.items()
        }

        # Compare with targets
        targets = {
            AllocationBucket.LONG_TERM.value: settings.ALLOCATION_LONG_TERM_PCT,
            AllocationBucket.TACTICAL.value: settings.ALLOCATION_TACTICAL_PCT,
            AllocationBucket.CRYPTO.value: settings.ALLOCATION_CRYPTO_PCT,
            AllocationBucket.LIQUIDITY.value: settings.ALLOCATION_LIQUIDITY_PCT,
        }

        deviations = {
            bucket: percentages[bucket] - targets[bucket]
            for bucket in targets
        }

        return {
            "total_wealth_eur": round(total_wealth, 2),
            "invested_equity_eur": round(invested_total, 2),
            "liquidity_eur": round(liquidity, 2),
            "buckets_eur": {k: round(v, 2) for k, v in buckets.items()},
            "actual_pct": {k: round(v * 100, 2) for k, v in percentages.items()},
            "target_pct": {k: round(v * 100, 2) for k, v in targets.items()},
            "deviations_pct": {k: round(v * 100, 2) for k, v in deviations.items()},
            "rebalance_required": any(abs(dev) > 0.05 for dev in deviations.values())
        }
