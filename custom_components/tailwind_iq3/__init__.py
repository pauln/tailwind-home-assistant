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
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, TAILWIND_COORDINATOR, UPDATE_INTERVAL, ATTR_RAW_STATE

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["cover"]


async def tailwind_get_status(hass: HomeAssistant, ip_address: str, api_token: str) -> str:
    websession = async_get_clientsession(hass)
    headers = {'TOKEN': api_token}
    async with websession.get(f"http://{ip_address}/status", headers=headers) as resp:
        assert resp.status == 200
        return await resp.text()


async def tailwind_send_command(
    hass: HomeAssistant, ip_address: str, api_token: str, command: str
) -> str:
    websession = async_get_clientsession(hass)
    headers = {'TOKEN': api_token}
    async with websession.post(f"http://{ip_address}/cmd", data=command, headers=headers) as resp:
        assert resp.status == 200
        return await resp.text()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up tailwind_iq3 from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    async def async_update_data():
        status = -1
        try:
            async with timeout(10):
                ip_address = entry.data[CONF_IP_ADDRESS]
                api_token = entry.data[CONF_API_TOKEN]
                status = await tailwind_get_status(hass, ip_address, api_token)

        except BaseException as error:
            raise UpdateFailed(error) from error

        _LOGGER.debug("tailwind reported state: %s", status)
        return {ATTR_RAW_STATE: int(status)}

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
