"""Support for Tailwind iQ3 Garage Door Openers."""
import logging

from homeassistant.components.cover import (
    DEVICE_CLASS_GARAGE,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    CoverEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_API_TOKEN,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import tailwind_send_command
from .const import CONF_NUM_DOORS, DOMAIN, TAILWIND_COORDINATOR
from .entity import TailwindEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up cover entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][TAILWIND_COORDINATOR]
    num_doors = config_entry.data.get(CONF_NUM_DOORS, 1)

    async_add_entities(
        [TailwindCover(hass, coordinator, device) for device in range(num_doors)]
    )


class TailwindCover(TailwindEntity, CoverEntity):
    """Representation of a Tailwind iQ3 cover."""

    _attr_supported_features = SUPPORT_OPEN | SUPPORT_CLOSE
    _attr_device_class = DEVICE_CLASS_GARAGE

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: DataUpdateCoordinator,
        device: DeviceEntry,
    ):
        """Initialize with API object, device id."""
        super().__init__(coordinator, device)
        self._hass = hass

    async def async_close_cover(self, **kwargs):
        """Issue close command to cover."""
        _LOGGER.info("Close door: %s", self._device)
        if self.is_closing or self.is_closed:
            return

        if self.coordinator.config_entry.data is None:
            return

        ip_address = self.coordinator.config_entry.data[CONF_IP_ADDRESS]
        api_token = self.coordinator.config_entry.data[CONF_API_TOKEN]
        command = 1 << self._device
        command = -1 * command
        response = await tailwind_send_command(
            self._hass, ip_address, api_token, str(command)
        )
        if response != "0" and int(response) != command:
            raise HomeAssistantError(
                f"Closing of cover {self._attr_name} failed with incorrect response: {response} (expected {command})"
            )

        # Write final state to HASS
        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs):
        """Issue open command to cover."""
        _LOGGER.info("Open door: %s", self._device)
        if self.is_opening or self.is_open:
            return

        if self.coordinator.config_entry.data is None:
            return

        ip_address = self.coordinator.config_entry.data[CONF_IP_ADDRESS]
        api_token = self.coordinator.config_entry.data[CONF_API_TOKEN]
        command = 1 << self._device
        response = await tailwind_send_command(
            self._hass, ip_address, api_token, str(command)
        )
        if response != "0" and int(response) != command:
            raise HomeAssistantError(
                f"Opening of cover {self._attr_name} failed with incorrect response: {response} (expected {command})"
            )

        # Write final state to HASS
        self.async_write_ha_state()
