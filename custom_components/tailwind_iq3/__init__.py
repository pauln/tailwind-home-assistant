"""The tailwind_iq3 integration."""
from __future__ import annotations
from async_timeout import timeout
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_API_TOKEN,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, TAILWIND_COORDINATOR, UPDATE_INTERVAL, ATTR_RAW_STATE
from aiotailwind import Auth, TailwindController

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["binary_sensor", "cover"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up tailwind_iq3 from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    async def async_update_data():
        try:
            async with timeout(10):
                ip_address = entry.data[CONF_IP_ADDRESS]
                api_token = entry.data[CONF_API_TOKEN]
                websession = async_get_clientsession(hass)
                auth = Auth(websession, ip_address, api_token)
                controller = TailwindController({}, auth)
                await controller.async_update()
                _LOGGER.debug("door status: " + ", ".join(["open" if door.is_open else "closed" for door in controller.doors]))
                return {ATTR_RAW_STATE: controller.doors}

        except BaseException as error:
            raise UpdateFailed(error) from error


    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="tailwind devices",
        update_method=async_update_data,
        update_interval=timedelta(seconds=UPDATE_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {TAILWIND_COORDINATOR: coordinator}
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
