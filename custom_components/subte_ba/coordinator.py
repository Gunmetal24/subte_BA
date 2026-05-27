"""Coordinators para Subte Buenos Aires."""
from __future__ import annotations

import logging
from datetime import timedelta

import requests
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_ALERTS,
    API_FORECAST,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_SCAN_INTERVAL_ALERTS,
    CONF_SCAN_INTERVAL_FORECAST,
    DEFAULT_SCAN_INTERVAL_ALERTS,
    DEFAULT_SCAN_INTERVAL_FORECAST,
    DOMAIN,
    LINEAS,
    STATE_NORMAL,
)

_LOGGER = logging.getLogger(__name__)
MAX_CONSECUTIVE_ERRORS = 3


class AlertsCoordinator(DataUpdateCoordinator):
    """Coordinator para alertas de servicio (cada ~120s)."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        self.client_id = entry.data[CONF_CLIENT_ID]
        self.client_secret = entry.data[CONF_CLIENT_SECRET]
        self._last_known: dict | None = None
        self._errors: int = 0

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_alerts",
            update_interval=timedelta(
                seconds=entry.data.get(CONF_SCAN_INTERVAL_ALERTS, DEFAULT_SCAN_INTERVAL_ALERTS)
            ),
        )

    async def _async_update_data(self) -> dict:
        try:
            data = await self.hass.async_add_executor_job(self._fetch)
            self._errors = 0
            self._last_known = data
            return data
        except Exception as err:
            self._errors += 1
            _LOGGER.warning("Alerts error %d/%d: %s", self._errors, MAX_CONSECUTIVE_ERRORS, err)
            if self._last_known and self._errors <= MAX_CONSECUTIVE_ERRORS:
                return self._last_known
            raise UpdateFailed(str(err)) from err

    def _fetch(self) -> dict:
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "json": "1",
        }
        r = requests.get(API_ALERTS, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

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


class ForecastCoordinator(DataUpdateCoordinator):
    """Coordinator para forecast de llegadas (cada ~30s)."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        self.client_id = entry.data[CONF_CLIENT_ID]
        self.client_secret = entry.data[CONF_CLIENT_SECRET]
        self._last_known: list | None = None
        self._errors: int = 0

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_forecast",
            update_interval=timedelta(
                seconds=entry.data.get(CONF_SCAN_INTERVAL_FORECAST, DEFAULT_SCAN_INTERVAL_FORECAST)
            ),
        )

    async def _async_update_data(self) -> list:
        try:
            data = await self.hass.async_add_executor_job(self._fetch)
            self._errors = 0
            self._last_known = data
            return data
        except Exception as err:
            self._errors += 1
            _LOGGER.warning("Forecast error %d/%d: %s", self._errors, MAX_CONSECUTIVE_ERRORS, err)
            if self._last_known and self._errors <= MAX_CONSECUTIVE_ERRORS:
                return self._last_known
            raise UpdateFailed(str(err)) from err

    def _fetch(self) -> list:
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "json": "1",
        }
        r = requests.get(API_FORECAST, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("Entity", [])
