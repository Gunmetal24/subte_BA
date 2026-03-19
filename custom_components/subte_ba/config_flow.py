"""Config flow para Subte Buenos Aires."""
from __future__ import annotations

import logging

import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import API_ALERTS, CONF_CLIENT_ID, CONF_CLIENT_SECRET, DOMAIN

_LOGGER = logging.getLogger(__name__)


def validate_credentials(client_id: str, client_secret: str) -> bool:
    """Validar que las credenciales funcionan contra la API."""
    params = {"client_id": client_id, "client_secret": client_secret, "json": "1"}
    response = requests.get(API_ALERTS, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    # Si devuelve un dict con 'entity' (aunque sea vacío), las credenciales son válidas
    return isinstance(data, dict) and "entity" in data


class SubteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow para configurar la integración via UI."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Primer paso: pedir client_id y client_secret."""
        errors = {}

        if user_input is not None:
            client_id = user_input[CONF_CLIENT_ID].strip()
            client_secret = user_input[CONF_CLIENT_SECRET].strip()

            try:
                valid = await self.hass.async_add_executor_job(
                    validate_credentials, client_id, client_secret
                )
                if valid:
                    await self.async_set_unique_id(client_id)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="Subte Buenos Aires",
                        data={
                            CONF_CLIENT_ID: client_id,
                            CONF_CLIENT_SECRET: client_secret,
                        },
                    )
                else:
                    errors["base"] = "invalid_auth"
            except requests.exceptions.ConnectionError:
                errors["base"] = "cannot_connect"
            except requests.exceptions.HTTPError as err:
                if err.response.status_code in (401, 403):
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Error inesperado al validar credenciales")
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(CONF_CLIENT_ID): str,
                vol.Required(CONF_CLIENT_SECRET): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "api_url": "https://buenosaires.gob.ar/desarrollourbano/transporte/apitransporte"
            },
        )
