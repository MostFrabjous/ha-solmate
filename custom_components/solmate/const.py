from dataclasses import dataclass, field
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfPower, PERCENTAGE, UnitOfTemperature, UnitOfTime

DOMAIN = "solmate"
DEFAULT_URI = "ws://solmate:9124/"
CONF_SERIAL = "serial_num"
CONF_URI = "uri"
UPDATE_INTERVAL = 30  # seconds


@dataclass
class SolmateSensorDescription:
    key: str
    name: str
    source: str  # which API route this comes from
    unit: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    value_fn: object = field(default=lambda x: x)


SENSOR_DESCRIPTIONS: list[SolmateSensorDescription] = [
    # live_values
    SolmateSensorDescription(
        key="pv_power",
        name="PV Power",
        source="live_values",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SolmateSensorDescription(
        key="inject_power",
        name="Injection Power",
        source="live_values",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SolmateSensorDescription(
        key="battery_state",
        name="Battery",
        source="live_values",
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda x: round(x * 100, 1),
    ),
    SolmateSensorDescription(
        key="battery_flow",
        name="Battery Flow",
        source="live_values",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SolmateSensorDescription(
        key="temperature",
        name="Temperature",
        source="live_values",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # get_injection_settings
    SolmateSensorDescription(
        key="user_minimum_injection",
        name="Minimum Injection",
        source="get_injection_settings",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SolmateSensorDescription(
        key="user_maximum_injection",
        name="Maximum Injection",
        source="get_injection_settings",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SolmateSensorDescription(
        key="user_minimum_battery_percentage",
        name="Minimum Battery Percentage",
        source="get_injection_settings",
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # get_boost_injection
    SolmateSensorDescription(
        key="remaining_time",
        name="Boost Remaining Time",
        source="get_boost_injection",
        unit=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SolmateSensorDescription(
        key="actual_wattage",
        name="Boost Actual Wattage",
        source="get_boost_injection",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
]
