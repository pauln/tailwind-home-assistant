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

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "Tailwind",
            "model": "iQ3",
        }

    @property
    def name(self):
        # Default name to match Tailwind app's default names.
        door_letter = ["A", "B", "C"][self._device]
        return f"Garage {door_letter}"

    @property
    def unique_id(self):
        # Set unique ID based on device unique ID and door number.
        coordinator_id = self.coordinator.config_entry.unique_id.replace(
            "tailwind-", ""
        )
        return f"{coordinator_id}_door_{self._device}"
