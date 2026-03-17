"""DataUpdateCoordinator for Petrol Price add-on API."""

from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_PATH_PRICES

_LOGGER = logging.getLogger(__name__)


class PetrolPriceCoordinator(DataUpdateCoordinator[list[dict]]):
    """Fetch fuel prices from the Petrol Price add-on API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_base_url: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name="petrolprice",
            update_interval=update_interval,
        )
        self._api_base_url = api_base_url.rstrip("/")

    async def _async_update_data(self) -> list[dict]:
        """Fetch prices from add-on API."""
        url = f"{self._api_base_url}{API_PATH_PRICES}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"HTTP {resp.status}")
                    data = await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(str(err)) from err

        prices = data.get("prices")
        if prices is None:
            raise UpdateFailed("Response missing 'prices'")
        if not isinstance(prices, list):
            raise UpdateFailed("'prices' is not a list")

        # Normalize to list of {fuel_type, price}; keep last known on error
        result = []
        for item in prices:
            if isinstance(item, dict) and "fuel_type" in item and "price" in item:
                try:
                    result.append({
                        "fuel_type": str(item["fuel_type"]).strip(),
                        "price": float(item["price"]),
                    })
                except (TypeError, ValueError):
                    continue
        return result
