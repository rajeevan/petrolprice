"""Petrol Price integration: polls add-on API and creates sensor entities."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_API_BASE_URL, CONF_SCAN_INTERVAL_HOURS, DOMAIN
from .coordinator import PetrolPriceCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Petrol Price from a config entry."""
    api_base_url = entry.data[CONF_API_BASE_URL].rstrip("/")
    scan_hours = entry.options.get(CONF_SCAN_INTERVAL_HOURS) or entry.data.get(
        CONF_SCAN_INTERVAL_HOURS, 6.0
    )
    update_interval = timedelta(hours=scan_hours)

    coordinator = PetrolPriceCoordinator(hass, api_base_url, update_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    ):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
