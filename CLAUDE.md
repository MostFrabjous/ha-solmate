# ha-solmate

Home Assistant custom integration for the EET SolMate solar battery system.

## Structure

```
custom_components/solmate/
├── __init__.py       # Setup + service registration
├── manifest.json
├── config_flow.py    # UI wizard: URI, serial, password
├── coordinator.py    # SolmateCoordinator (DataUpdateCoordinator)
├── sensor.py         # One SolmateSensor per SENSOR_DESCRIPTIONS entry
├── const.py          # DOMAIN, sensor descriptions, defaults
├── strings.json      # UI labels (source of truth)
└── translations/en.json
```

## Device

- URI: `ws://sun2plug.beeb.at:9124/` (local) or `ws://10.0.0.40:9124/`
- Serial and password: never hardcode — use config entry
- API: local WebSocket, 3-step auth (login → signature → authenticate per session)

## battery_state

Raw API value is a fraction (0.07 = 7%). `const.py` applies `× 100` via `value_fn`.

## Deploying to HA for testing

```bash
cp -r custom_components/solmate \
  ~/Remote/truenas-app-mounts/home-assistant/config/custom_components/
```

Then restart HA and add the integration under Settings → Integrations.

## Planned (v2)

- `logs` route for historical data
- `number` entities for injection limits (instead of services)
