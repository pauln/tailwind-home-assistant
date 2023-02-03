"""Support for Tailwind iQ3 Garage Door Openers."""
import logging

from homeassistant.components.cover import (
    DEVICE_CLASS_GARAGE,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    CoverEntity,
)
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_API_TOKEN,
)
from homeassistant.exceptions import HomeAssistantError

from . import tailwind_send_command
from .const import CONF_NUM_DOORS, DOMAIN, TAILWIND_COORDINATOR, ATTR_RAW_STATE
from .entity import TailwindEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up cover entities."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    conf = config_entry.data
    coordinator = data[TAILWIND_COORDINATOR]
    num_doors = conf[CONF_NUM_DOORS] if CONF_NUM_DOORS in conf else 1

    async_add_entities(
        [TailwindCover(hass, coordinator, device) for device in range(num_doors)]
    )


class TailwindCover(TailwindEntity, CoverEntity):
    """Representation of a Tailwind iQ3 cover."""

    _attr_supported_features = SUPPORT_OPEN | SUPPORT_CLOSE
    _attr_device_class = DEVICE_CLASS_GARAGE

    def __init__(self, hass, coordinator, device):
        """Initialize with API object, device id."""
        super().__init__(coordinator, device)
        self._hass = hass

    @property
    def is_closed(self):
        if self.coordinator.data is None:
            return None

        if self.coordinator.data[ATTR_RAW_STATE] == -1:
            return None

        return not self.is_open

    @property
    def is_closing(self):
        """Return if the cover is closing or not."""
        return False

    @property
    def is_open(self):
        if self.coordinator.data is None:
            return None

        if self.coordinator.data[ATTR_RAW_STATE] == -1:
            return None

        raw_state = self.coordinator.data[ATTR_RAW_STATE]
        bit_pos = 1 << self._device

        """Return true if cover is open, else False."""
        return raw_state & bit_pos

    @property
    def is_opening(self):
        """Return if the cover is opening or not."""
        return False

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
