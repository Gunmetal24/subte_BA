"""Config flow para Subte Buenos Aires."""
from __future__ import annotations

import logging

import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

from .const import (
    API_ALERTS,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_ESTACION,
    CONF_SCAN_INTERVAL_ALERTS,
    CONF_SCAN_INTERVAL_FORECAST,
    DEFAULT_SCAN_INTERVAL_ALERTS,
    DEFAULT_SCAN_INTERVAL_FORECAST,
    DOMAIN,
    ESTACIONES_SELECTOR,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

# Opciones para el selector: lista de "Línea X - Estación"
ESTACION_OPTIONS = list(ESTACIONES_SELECTOR.keys())


def validate_credentials(client_id: str, client_secret: str) -> bool:
    params = {"client_id": client_id, "client_secret": client_secret, "json": "1"}
    r = requests.get(API_ALERTS, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    return isinstance(data, dict) and "entity" in data


class SubteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            client_id = user_input[CONF_CLIENT_ID].strip()
            client_secret = user_input[CONF_CLIENT_SECRET].strip()
            estacion_label = user_input.get(CONF_ESTACION, "")
            # Convertir "Línea A - Puán" → "Puán"
            estacion_nombre = ESTACIONES_SELECTOR.get(estacion_label) if estacion_label else None

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
                            CONF_SCAN_INTERVAL_ALERTS: user_input[CONF_SCAN_INTERVAL_ALERTS],
                            CONF_SCAN_INTERVAL_FORECAST: user_input[CONF_SCAN_INTERVAL_FORECAST],
                            CONF_ESTACION: estacion_nombre,
                        },
                    )
                else:
                    errors["base"] = "invalid_auth"
            except requests.exceptions.ConnectionError:
                errors["base"] = "cannot_connect"
            except requests.exceptions.HTTPError as err:
                errors["base"] = "invalid_auth" if err.response.status_code in (401, 403) else "cannot_connect"
            except Exception:
                _LOGGER.exception("Error inesperado")
                errors["base"] = "unknown"

        schema = vol.Schema({
            vol.Required(CONF_CLIENT_ID): str,
            vol.Required(CONF_CLIENT_SECRET): str,
            vol.Optional(CONF_SCAN_INTERVAL_ALERTS, default=DEFAULT_SCAN_INTERVAL_ALERTS): vol.All(
                int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
            ),
            vol.Optional(CONF_SCAN_INTERVAL_FORECAST, default=DEFAULT_SCAN_INTERVAL_FORECAST): vol.All(
                int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
            ),
            vol.Optional(CONF_ESTACION, default=""): SelectSelector(
                SelectSelectorConfig(
                    options=[""] + ESTACION_OPTIONS,
                    mode=SelectSelectorMode.DROPDOWN,
                    translation_key="estacion",
                )
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "api_url": "https://buenosaires.gob.ar/desarrollourbano/transporte/apitransporte",
                "min_interval": str(MIN_SCAN_INTERVAL),
                "max_interval": str(MAX_SCAN_INTERVAL),
            },
        )
