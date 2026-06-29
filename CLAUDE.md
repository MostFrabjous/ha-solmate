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

- URI: `ws://sun2plug.beeb.at:9124/` or `ws://10.0.0.40:9124/`
- Serial and password: never hardcode — use config entry
- API: local WebSocket, 3-step auth (login → signature → authenticate per session)
- Credentials for testing: see HA config entry or ask Henry

## battery_state

Raw API value is a fraction (0.07 = 7%). `const.py` applies `× 100` via `value_fn`.

## Deploying to HA for testing

`~/Remote/truenas-app-mounts` is an sshfs mount — `custom_components/` is owned by root so cp fails.
Use scp instead:

```bash
scp -r custom_components/solmate admin@10.0.0.10:/mnt/.ix-apps/app_mounts/home-assistant/config/custom_components/
```

Then restart HA: Settings → System → Restart.
Add integration: Settings → Integrations → Add Integration → search "SolMate".

HA is at https://home.beeb.at — TrueNAS at 10.0.0.10.

## Current status

- Code written, not yet deployed or tested
- Next: deploy via scp, restart HA, configure integration, verify sensors

## Publishing

- Codeberg: https://codeberg.org (account: frabjous@mailbox.org)
- Repo name: `ha-solmate`
- Also mirror to GitHub for HACS discoverability
- Update `manifest.json` documentation/issue_tracker URLs once repo is live

## Planned (v2)

- `logs` route for historical data
- `number` entities for injection limits (instead of services)
