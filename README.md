# EET SolMate — Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)

Home Assistant custom integration for the [EET SolMate](https://eet.energy) solar battery system.

## Features

- **Sensors**: PV power, injection power, battery state, battery flow, temperature
- **Settings sensors**: min/max injection, minimum battery percentage, boost status
- **Services**: control injection limits, minimum battery percentage, and boost injection

## Installation

### HACS (recommended)

1. Add this repository as a custom repository in HACS
2. Install **EET SolMate**
3. Restart Home Assistant
4. Go to **Settings → Integrations → Add Integration** and search for *SolMate*

### Manual

Copy `custom_components/solmate/` to your HA config directory under `custom_components/`.

## Configuration

| Field | Description |
|---|---|
| WebSocket URI | URI of your SolMate, e.g. `ws://solmate:9124/` or `ws://10.0.0.40:9124/` |
| Serial Number | Printed on the device |
| Password | Your SolMate password |

## Services

### `solmate.set_minimum_injection`
Set minimum injection power (0–200 W).
```yaml
service: solmate.set_minimum_injection
data:
  injection: 30
```

### `solmate.set_maximum_injection`
Set maximum injection power (0–800 W).
```yaml
service: solmate.set_maximum_injection
data:
  injection: 600
```

### `solmate.set_minimum_battery_percentage`
Set minimum battery percentage before injection starts.
```yaml
service: solmate.set_minimum_battery_percentage
data:
  battery_percentage: 20
```

### `solmate.set_boost_injection`
Temporarily boost injection to a given wattage. Set `set_time: 0` to deactivate.
```yaml
service: solmate.set_boost_injection
data:
  set_wattage: 800
  set_time: 3600  # seconds
```

## Notes

- The SolMate API is local WebSocket only — no cloud dependency
- `battery_state` sensor shows percentage (the raw API value is a fraction)
- `battery_flow` is positive when charging, negative when discharging
- Historical data (`logs` route) is planned for a future release
