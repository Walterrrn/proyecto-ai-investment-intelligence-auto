"""Federal Reserve Economic Data (FRED) macroeconomic collector."""

from datetime import date, datetime
from typing import List, Optional
import httpx
from src.core.config import settings
from src.core.telemetry import logger
from src.services.market_data.schemas import MacroObservationDTO


class FredMacroCollector:
    """Fetches macroeconomic indicators from St. Louis Fed (FRED) API."""

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    # Default series relevant to macro asset allocation
    CORE_SERIES = {
        "FEDFUNDS": "Effective Federal Funds Rate (%)",
        "T10Y2Y": "10-Year minus 2-Year Treasury Yield Spread (%)",
        "CPIAUCSL": "Consumer Price Index for All Urban Consumers",
        "UNRATE": "Civilian Unemployment Rate (%)",
    }

    # Fallback reference values if no API key is provided
    FALLBACK_OBSERVATIONS = {
        "FEDFUNDS": 4.58,
        "T10Y2Y": 0.18,
        "CPIAUCSL": 315.3,
        "UNRATE": 4.1,
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.FRED_API_KEY

    async def fetch_series_observations(
        self,
        series_id: str,
        limit: int = 30
    ) -> List[MacroObservationDTO]:
        """Fetch observations for a given FRED series ID."""
        if not self.api_key:
            logger.info("fred_no_api_key_using_baseline", series_id=series_id)
            fallback_val = self.FALLBACK_OBSERVATIONS.get(series_id, 0.0)
            return [
                MacroObservationDTO(
                    series_id=series_id,
                    period_date=date.today(),
                    value=fallback_val,
                    units="Baseline",
                )
            ]

        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()

            observations: List[MacroObservationDTO] = []
            for item in data.get("observations", []):
                val_str = item.get("value")
                if val_str in (None, ".", ""):
                    continue
                try:
                    val = float(val_str)
                    obs_date = datetime.strptime(item["date"], "%Y-%m-%d").date()
                    observations.append(
                        MacroObservationDTO(
                            series_id=series_id,
                            period_date=obs_date,
                            value=val,
                            units=self.CORE_SERIES.get(series_id, "Index"),
                        )
                    )
                except (ValueError, KeyError):
                    continue

            return observations

        except Exception as exc:
            logger.error("fred_fetch_error", series_id=series_id, error=str(exc))
            # Return baseline fallback on error
            val = self.FALLBACK_OBSERVATIONS.get(series_id, 0.0)
            return [
                MacroObservationDTO(
                    series_id=series_id,
                    period_date=date.today(),
                    value=val,
                    units="Fallback",
                )
            ]

    async def fetch_core_macro_snapshot(self) -> List[MacroObservationDTO]:
        """Fetch latest snapshot of all core macroeconomic indicators."""
        results: List[MacroObservationDTO] = []
        for sid in self.CORE_SERIES.keys():
            obs_list = await self.fetch_series_observations(sid, limit=1)
            if obs_list:
                results.append(obs_list[0])
        return results
