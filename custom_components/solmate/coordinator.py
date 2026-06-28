import asyncio
import base64
import hashlib
import json
import logging
import random
from datetime import timedelta

import websockets
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

POLL_ROUTES = ["live_values", "get_injection_settings", "get_boost_injection"]


class SolmateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, uri: str, serial: str, password: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self._uri = uri
        self._serial = serial
        self._password = password
        self._signature: str | None = None

    def _pw_hash(self) -> str:
        return base64.encodebytes(
            hashlib.sha256(self._password.encode()).digest()
        ).decode()

    async def _login(self) -> str:
        msg_id = random.randint(1000, 9999)
        async with websockets.connect(self._uri) as ws:
            await ws.send(json.dumps({
                "route": "login", "id": msg_id,
                "data": {
                    "device_id": "web",
                    "serial_num": self._serial,
                    "user_password_hash": self._pw_hash(),
                },
            }))
            response = json.loads(await ws.recv())
        self._signature = response["data"]["signature"]
        _LOGGER.debug("SolMate login successful")
        return self._signature

    async def _authenticated_request(self, routes: list[str], write_route: str | None = None, write_data: dict | None = None) -> dict:
        if not self._signature:
            await self._login()

        msg_id = random.randint(1000, 9999)
        results = {}

        async with websockets.connect(self._uri) as ws:
            # Authenticate
            await ws.send(json.dumps({
                "route": "authenticate", "id": msg_id,
                "data": {
                    "device_id": "web",
                    "serial_num": self._serial,
                    "signature": self._signature,
                },
            }))
            auth_r = json.loads(await ws.recv())

            if not auth_r.get("data", {}).get("success"):
                _LOGGER.debug("SolMate signature expired, re-logging in")
                await self._login()
                await ws.send(json.dumps({
                    "route": "authenticate", "id": msg_id,
                    "data": {
                        "device_id": "web",
                        "serial_num": self._serial,
                        "signature": self._signature,
                    },
                }))
                json.loads(await ws.recv())

            for route in routes:
                await ws.send(json.dumps({"route": route, "id": msg_id}))
                r = json.loads(await ws.recv())
                results[route] = r.get("data", {})

            if write_route is not None:
                await ws.send(json.dumps({"route": write_route, "id": msg_id, "data": write_data or {}}))
                r = json.loads(await ws.recv())
                results[write_route] = r.get("data", {})

        return results

    async def _async_update_data(self) -> dict:
        try:
            return await self._authenticated_request(POLL_ROUTES)
        except Exception as err:
            self._signature = None
            raise UpdateFailed(f"SolMate communication error: {err}") from err

    async def async_send_command(self, route: str, data: dict) -> bool:
        """Send a write command to the SolMate. Returns True on success."""
        try:
            result = await self._authenticated_request([], write_route=route, write_data=data)
            return result.get(route, {}).get("success", False)
        except Exception as err:
            self._signature = None
            _LOGGER.error("SolMate command %s failed: %s", route, err)
            return False
