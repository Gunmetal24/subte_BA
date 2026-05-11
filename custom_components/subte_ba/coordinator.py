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
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LINEAS,
    STATE_NORMAL,
)

_LOGGER = logging.getLogger(__name__)

# Cuántos errores consecutivos tolerar antes de marcar unavailable
MAX_CONSECUTIVE_ERRORS = 3


class SubteCoordinator(DataUpdateCoordinator):
    """Coordina el polling de la API del GCBA."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Inicializar el coordinator."""
        self.client_id = entry.data[CONF_CLIENT_ID]
        self.client_secret = entry.data[CONF_CLIENT_SECRET]
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        self._last_known_data: dict | None = None
        self._consecutive_errors: int = 0

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict:
        """Obtener datos de la API."""
        try:
            data = await self.hass.async_add_executor_job(self._fetch_alerts)
            # Éxito: resetear contador y guardar último valor conocido
            self._consecutive_errors = 0
            self._last_known_data = data
            return data

        except requests.exceptions.HTTPError as err:
            self._consecutive_errors += 1
            status = err.response.status_code if err.response is not None else "?"
            _LOGGER.warning(
                "Error HTTP %s de la API del GCBA (intento %d/%d). %s",
                status,
                self._consecutive_errors,
                MAX_CONSECUTIVE_ERRORS,
                "Usando último valor conocido." if self._last_known_data else "Sin datos previos.",
            )
            if self._last_known_data and self._consecutive_errors <= MAX_CONSECUTIVE_ERRORS:
                return self._last_known_data
            raise UpdateFailed(f"Error HTTP {status} tras {self._consecutive_errors} intentos.") from err

        except requests.exceptions.Timeout:
            self._consecutive_errors += 1
            _LOGGER.warning(
                "Timeout al consultar la API (intento %d/%d). %s",
                self._consecutive_errors,
                MAX_CONSECUTIVE_ERRORS,
                "Usando último valor conocido." if self._last_known_data else "Sin datos previos.",
            )
            if self._last_known_data and self._consecutive_errors <= MAX_CONSECUTIVE_ERRORS:
                return self._last_known_data
            raise UpdateFailed(f"Timeout tras {self._consecutive_errors} intentos consecutivos.") from None

        except Exception as err:
            self._consecutive_errors += 1
            _LOGGER.warning(
                "Error inesperado al consultar la API (intento %d/%d): %s",
                self._consecutive_errors,
                MAX_CONSECUTIVE_ERRORS,
                err,
            )
            if self._last_known_data and self._consecutive_errors <= MAX_CONSECUTIVE_ERRORS:
                return self._last_known_data
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
