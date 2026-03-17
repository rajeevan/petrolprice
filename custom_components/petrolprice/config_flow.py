"""Config flow for Petrol Price integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_API_BASE_URL,
    CONF_SCAN_INTERVAL_HOURS,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_BASE_URL): str,
        vol.Required(
            CONF_SCAN_INTERVAL_HOURS,
            default=DEFAULT_SCAN_INTERVAL_HOURS,
        ): vol.All(vol.Coerce(float), vol.Range(min=0.25, max=168)),
    }
)


async def validate_url(hass: HomeAssistant, url: str) -> str | None:
    """Validate add-on API URL by requesting /api/prices."""
    import aiohttp
    base = url.rstrip("/")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base}/api/prices",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    return f"HTTP {resp.status}"
                data = await resp.json()
                if "prices" not in data:
                    return "Invalid response: missing 'prices'"
                return None
    except aiohttp.ClientError as e:
        return str(e)
    except Exception as e:
        return str(e)


class PetrolPriceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Petrol Price."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            url = (user_input.get(CONF_API_BASE_URL) or "").strip()
            if not url:
                errors["base"] = "api_url_required"
            else:
                if err := await validate_url(self.hass, url):
                    errors["base"] = "cannot_connect"
                    _LOGGER.warning("Validation failed for %s: %s", url, err)
                else:
                    return self.async_create_entry(
                        title="Petrol Price",
                        data={
                            CONF_API_BASE_URL: url,
                            CONF_SCAN_INTERVAL_HOURS: user_input.get(
                                CONF_SCAN_INTERVAL_HOURS,
                                DEFAULT_SCAN_INTERVAL_HOURS,
                            ),
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
            description_placeholders={
                "ingress_help": "Use the add-on's Web UI URL (ingress), e.g. from the add-on panel in Home Assistant.",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> PetrolPriceOptionsFlow:
        """Get the options flow for this handler."""
        return PetrolPriceOptionsFlow(config_entry)


class PetrolPriceOptionsFlow(config_entries.OptionsFlow):
    """Handle Petrol Price options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL_HOURS,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL_HOURS
                        )
                        or self.config_entry.data.get(
                            CONF_SCAN_INTERVAL_HOURS,
                            DEFAULT_SCAN_INTERVAL_HOURS,
                        ),
                    ): vol.All(vol.Coerce(float), vol.Range(min=0.25, max=168)),
                }
            ),
        )
