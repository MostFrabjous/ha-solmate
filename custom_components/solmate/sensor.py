from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_DESCRIPTIONS, SolmateSensorDescription
from .coordinator import SolmateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SolmateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SolmateSensor(coordinator, entry, desc)
        for desc in SENSOR_DESCRIPTIONS
        if desc.source in coordinator.data and desc.key in coordinator.data[desc.source]
    )


class SolmateSensor(CoordinatorEntity[SolmateCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SolmateCoordinator,
        entry: ConfigEntry,
        description: SolmateSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self._description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="SolMate",
            manufacturer="EET Energy",
            model="SolMate",
        )

    @property
    def native_value(self):
        raw = self.coordinator.data.get(self._description.source, {}).get(self._description.key)
        if raw is None:
            return None
        return self._description.value_fn(raw)
