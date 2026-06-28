import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD

from .const import DOMAIN, DEFAULT_URI, CONF_SERIAL, CONF_URI
from .coordinator import SolmateCoordinator


class SolmateConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            coordinator = SolmateCoordinator(
                self.hass,
                uri=user_input[CONF_URI],
                serial=user_input[CONF_SERIAL],
                password=user_input[CONF_PASSWORD],
            )
            try:
                await coordinator._login()
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input[CONF_SERIAL])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"SolMate {user_input[CONF_SERIAL]}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_URI, default=DEFAULT_URI): str,
                vol.Required(CONF_SERIAL): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )
