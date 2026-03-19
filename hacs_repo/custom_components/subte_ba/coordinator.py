"""DataUpdateCoordinator para Subte Buenos Aires."""
from __future__ import annotations

import logging
from datetime import timedelta

import requests
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_ALERTS,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LINEAS,
    STATE_NORMAL,
)

_LOGGER = logging.getLogger(__name__)


class SubteCoordinator(DataUpdateCoordinator):
    """Coordina el polling de la API del GCBA."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Inicializar el coordinator."""
        self.client_id = entry.data[CONF_CLIENT_ID]
        self.client_secret = entry.data[CONF_CLIENT_SECRET]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        """Obtener datos de la API."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_alerts)
        except Exception as err:
            raise UpdateFailed(f"Error al consultar la API: {err}") from err

    def _fetch_alerts(self) -> dict:
        """Hacer el request a la API (bloqueante, se ejecuta en thread pool)."""
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "json": "1",
        }

        response = requests.get(API_ALERTS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Inicializar todas las líneas como Normal
        alertas = {linea: {"estado": STATE_NORMAL, "detalle": ""} for linea in LINEAS}

        for entity in data.get("entity", []):
            alert = entity.get("alert", {})
            translations = alert.get("header_text", {}).get("translation", [])
            texto = translations[0]["text"] if translations else "Alerta activa"

            for informed in alert.get("informed_entity", []):
                route = informed.get("route_id", "")
                if route in alertas:
                    alertas[route] = {
                        "estado": texto,
                        "detalle": alert.get("description_text", {})
                        .get("translation", [{}])[0]
                        .get("text", ""),
                    }

        return alertas
