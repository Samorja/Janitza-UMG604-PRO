"""Sensor platform for the Janitza UMG 604-PRO."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfReactivePower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import JanitzaConfigEntry
from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import JanitzaCoordinator


@dataclass(frozen=True, kw_only=True)
class JanitzaSensorEntityDescription(SensorEntityDescription):
    """Sensor description with the Modbus start register of the float value."""

    register: int


def _phases(
    key: str,
    name: str,
    start: int,
    labels: tuple[str, ...] = ("L1", "L2", "L3"),
    **kwargs,
) -> list[JanitzaSensorEntityDescription]:
    """Build one description per phase from consecutive float registers."""
    return [
        JanitzaSensorEntityDescription(
            key=f"{key}_{label.lower().replace('-', '_')}",
            name=f"{name} {label}",
            register=start + 2 * index,
            **kwargs,
        )
        for index, label in enumerate(labels)
    ]


_VOLTAGE = {
    "device_class": SensorDeviceClass.VOLTAGE,
    "native_unit_of_measurement": UnitOfElectricPotential.VOLT,
    "state_class": SensorStateClass.MEASUREMENT,
    "suggested_display_precision": 1,
}
_CURRENT = {
    "device_class": SensorDeviceClass.CURRENT,
    "native_unit_of_measurement": UnitOfElectricCurrent.AMPERE,
    "state_class": SensorStateClass.MEASUREMENT,
    "suggested_display_precision": 2,
}
_POWER = {
    "device_class": SensorDeviceClass.POWER,
    "native_unit_of_measurement": UnitOfPower.WATT,
    "state_class": SensorStateClass.MEASUREMENT,
    "suggested_display_precision": 0,
}
_APPARENT = {
    "device_class": SensorDeviceClass.APPARENT_POWER,
    "native_unit_of_measurement": UnitOfApparentPower.VOLT_AMPERE,
    "state_class": SensorStateClass.MEASUREMENT,
    "suggested_display_precision": 0,
}
_REACTIVE = {
    "device_class": SensorDeviceClass.REACTIVE_POWER,
    "native_unit_of_measurement": UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
    "state_class": SensorStateClass.MEASUREMENT,
    "suggested_display_precision": 0,
}
_POWER_FACTOR = {
    "device_class": SensorDeviceClass.POWER_FACTOR,
    "state_class": SensorStateClass.MEASUREMENT,
    "suggested_display_precision": 2,
}
_ENERGY = {
    "device_class": SensorDeviceClass.ENERGY,
    "native_unit_of_measurement": UnitOfEnergy.WATT_HOUR,
    "suggested_unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
    "suggested_display_precision": 2,
}
_THD = {
    "native_unit_of_measurement": PERCENTAGE,
    "state_class": SensorStateClass.MEASUREMENT,
    "suggested_display_precision": 1,
}

# Register addresses follow the UMG 604 "frequently required measured values"
# table. Verify against the Modbus address list for your firmware.
SENSORS: tuple[JanitzaSensorEntityDescription, ...] = (
    *_phases("voltage", "Voltage", 19000, ("L1-N", "L2-N", "L3-N"), **_VOLTAGE),
    *_phases("voltage", "Voltage", 19006, ("L1-L2", "L2-L3", "L3-L1"), **_VOLTAGE),
    *_phases("current", "Current", 19012, **_CURRENT),
    JanitzaSensorEntityDescription(
        key="current_sum", name="Current sum", register=19018, **_CURRENT
    ),
    *_phases("active_power", "Active power", 19020, **_POWER),
    JanitzaSensorEntityDescription(
        key="active_power_sum", name="Active power sum", register=19026, **_POWER
    ),
    *_phases("apparent_power", "Apparent power", 19028, **_APPARENT),
    JanitzaSensorEntityDescription(
        key="apparent_power_sum", name="Apparent power sum", register=19034, **_APPARENT
    ),
    *_phases("reactive_power", "Reactive power", 19036, **_REACTIVE),
    JanitzaSensorEntityDescription(
        key="reactive_power_sum", name="Reactive power sum", register=19042, **_REACTIVE
    ),
    *_phases("power_factor", "Power factor", 19044, **_POWER_FACTOR),
    JanitzaSensorEntityDescription(
        key="frequency",
        name="Frequency",
        register=19050,
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    JanitzaSensorEntityDescription(
        key="energy_net",
        name="Active energy net",
        register=19060,
        state_class=SensorStateClass.TOTAL,
        **_ENERGY,
    ),
    JanitzaSensorEntityDescription(
        key="energy_import",
        name="Active energy import",
        register=19068,
        state_class=SensorStateClass.TOTAL_INCREASING,
        **_ENERGY,
    ),
    JanitzaSensorEntityDescription(
        key="energy_export",
        name="Active energy export",
        register=19076,
        state_class=SensorStateClass.TOTAL_INCREASING,
        **_ENERGY,
    ),
    *_phases("thd_voltage", "THD voltage", 19110, **_THD),
    *_phases("thd_current", "THD current", 19116, **_THD),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: JanitzaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create sensors for a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(JanitzaSensor(coordinator, description) for description in SENSORS)


class JanitzaSensor(CoordinatorEntity[JanitzaCoordinator], SensorEntity):
    """A single measured value of the UMG 604-PRO."""

    _attr_has_entity_name = True
    entity_description: JanitzaSensorEntityDescription

    def __init__(
        self,
        coordinator: JanitzaCoordinator,
        description: JanitzaSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=entry.title,
        )

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get(self.entity_description.register)
