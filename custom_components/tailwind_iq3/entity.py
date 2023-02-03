from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN


class TailwindEntity(CoordinatorEntity):
    """Base class for Tailwind iQ3 Entities."""

    def __init__(self, coordinator: DataUpdateCoordinator, device: DeviceEntry) -> None:
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = device.device_id

    @property
    def name(self):
        return self._device.name

    @property
    def device_info(self):
        device_info = {
            "identifiers": {(DOMAIN, self._device.device_id)},
            "name": self._device.name,
            "manufacturer": "Tailwind",
            "model": "iQ3",
        }
        if self._device.parent_device_id:
            device_info["via_device"] = (DOMAIN, self._device.parent_device_id)
        return device_info
