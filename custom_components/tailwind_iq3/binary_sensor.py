"""Binary sensor that indicates if the door is open or closed."""
import logging

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_GARAGE_DOOR,
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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
        [TailwindBinarySensor(hass, coordinator, device) for device in range(num_doors)]
    )


class TailwindBinarySensor(TailwindEntity, BinarySensorEntity):
    """Representation of a Tailwind iQ3 cover."""

    _attr_device_class = DEVICE_CLASS_GARAGE_DOOR

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: DataUpdateCoordinator,
        device: DeviceEntry,
    ):
        """Initialize with API object, device id."""
        super().__init__(coordinator, device)
        self._hass = hass

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return DEVICE_CLASS_GARAGE_DOOR

    @property
    def is_on(self) -> bool | None:
        return self.is_open
