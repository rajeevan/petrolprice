"""Sensor platform: one SensorEntity per fuel type from coordinator data."""

from __future__ import annotations

import re
import logging
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_UNIT, DOMAIN
from .coordinator import PetrolPriceCoordinator

_LOGGER = logging.getLogger(__name__)

# Slugify fuel type for entity_id and unique_id
def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_") or "unknown"


class PetrolPriceSensor(CoordinatorEntity[PetrolPriceCoordinator], SensorEntity):
    """Sensor for a single fuel type price."""

    _attr_native_unit_of_measurement = DEFAULT_UNIT
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: PetrolPriceCoordinator,
        entry: ConfigEntry,
        fuel_type: str,
        key: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._fuel_type = fuel_type
        self._key = key
        self._attr_name = fuel_type
        self._attr_unique_id = f"{entry.entry_id}_{key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Petrol Price",
            manufacturer="Petrol Price",
        )

    @property
    def native_value(self) -> float | None:
        """Return the price from coordinator data."""
        if not self.coordinator.data:
            return None
        for item in self.coordinator.data:
            if item.get("fuel_type") == self._fuel_type:
                return item.get("price")
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Petrol Price sensors from a config entry."""
    coordinator: PetrolPriceCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Build one sensor per fuel type; use fuel_type as display name and key for unique_id
    entities = []
    seen = set()
    for item in coordinator.data or []:
        fuel_type = item.get("fuel_type")
        if not fuel_type or fuel_type in seen:
            continue
        seen.add(fuel_type)
        key = _slug(fuel_type)
        entities.append(
            PetrolPriceSensor(coordinator, entry, fuel_type, key)
        )
    async_add_entities(entities)
    # When coordinator updates, we may get new fuel types; HA will not add entities
    # automatically. For dynamic add/remove we'd need to implement a listener and
    # async_add_entities again. For simplicity we only add entities at setup; new
    # fuel types after refresh will appear on next reload of the integration.
    if not entities and coordinator.data:
        _LOGGER.warning("No valid fuel types in coordinator data")
