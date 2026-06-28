import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_SERIAL, CONF_URI
from .coordinator import SolmateCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]

SERVICE_SET_MIN_INJECTION = "set_minimum_injection"
SERVICE_SET_MAX_INJECTION = "set_maximum_injection"
SERVICE_SET_MIN_BATTERY = "set_minimum_battery_percentage"
SERVICE_SET_BOOST = "set_boost_injection"

SERVICE_SET_MIN_INJECTION_SCHEMA = vol.Schema({
    vol.Required("injection"): vol.All(vol.Coerce(int), vol.Range(min=0, max=200)),
})
SERVICE_SET_MAX_INJECTION_SCHEMA = vol.Schema({
    vol.Required("injection"): vol.All(vol.Coerce(int), vol.Range(min=0, max=800)),
})
SERVICE_SET_MIN_BATTERY_SCHEMA = vol.Schema({
    vol.Required("battery_percentage"): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
})
SERVICE_SET_BOOST_SCHEMA = vol.Schema({
    vol.Required("set_wattage"): vol.All(vol.Coerce(int), vol.Range(min=0, max=800)),
    vol.Required("set_time"): vol.All(vol.Coerce(int), vol.Range(min=0)),
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = SolmateCoordinator(
        hass,
        uri=entry.data[CONF_URI],
        serial=entry.data[CONF_SERIAL],
        password=entry.data[CONF_PASSWORD],
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _register_services(hass, coordinator)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


def _register_services(hass: HomeAssistant, coordinator: SolmateCoordinator) -> None:
    async def handle_set_min_injection(call: ServiceCall) -> None:
        await coordinator.async_send_command(
            "set_user_minimum_injection", {"injection": call.data["injection"]}
        )
        await coordinator.async_request_refresh()

    async def handle_set_max_injection(call: ServiceCall) -> None:
        await coordinator.async_send_command(
            "set_user_maximum_injection", {"injection": call.data["injection"]}
        )
        await coordinator.async_request_refresh()

    async def handle_set_min_battery(call: ServiceCall) -> None:
        await coordinator.async_send_command(
            "set_user_minimum_battery_percentage",
            {"battery_percentage": call.data["battery_percentage"]},
        )
        await coordinator.async_request_refresh()

    async def handle_set_boost(call: ServiceCall) -> None:
        await coordinator.async_send_command(
            "set_boost_injection",
            {"set_wattage": call.data["set_wattage"], "set_time": call.data["set_time"]},
        )
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, SERVICE_SET_MIN_INJECTION, handle_set_min_injection, SERVICE_SET_MIN_INJECTION_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SET_MAX_INJECTION, handle_set_max_injection, SERVICE_SET_MAX_INJECTION_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SET_MIN_BATTERY, handle_set_min_battery, SERVICE_SET_MIN_BATTERY_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SET_BOOST, handle_set_boost, SERVICE_SET_BOOST_SCHEMA)
