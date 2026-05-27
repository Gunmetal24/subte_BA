"""Sensores para Subte Buenos Aires."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_ESTACION,
    DIRECTION_CABECERA,
    DIRECTION_CENTRO,
    DOMAIN,
    LINEAS,
    STATE_NORMAL,
)
from .coordinator import AlertsCoordinator, ForecastCoordinator

DEVICE_INFO = {
    "identifiers": {(DOMAIN, "subte_ba")},
    "name": "Subte Buenos Aires",
    "manufacturer": "GCBA / Emova",
    "model": "API Transporte GCBA",
    "entry_type": "service",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators = hass.data[DOMAIN][entry.entry_id]
    alerts_coord: AlertsCoordinator = coordinators["alerts"]
    forecast_coord: ForecastCoordinator = coordinators["forecast"]
    estacion = entry.data.get(CONF_ESTACION)

    entities = [
        SubteAlertSensor(alerts_coord, linea_id, linea_info)
        for linea_id, linea_info in LINEAS.items()
    ]

    if estacion:
        entities.append(SubteForecastSensor(forecast_coord, estacion, DIRECTION_CENTRO, "centro"))
        entities.append(SubteForecastSensor(forecast_coord, estacion, DIRECTION_CABECERA, "cabecera"))

    async_add_entities(entities)


class SubteAlertSensor(CoordinatorEntity, SensorEntity):
    """Sensor de alertas por línea."""

    def __init__(self, coordinator: AlertsCoordinator, linea_id: str, linea_info: dict):
        super().__init__(coordinator)
        self._linea_id = linea_id
        self._attr_name = linea_info["nombre"]
        self._attr_unique_id = f"subte_ba_{linea_id.lower()}"
        self._attr_icon = linea_info["icon"]
        self._linea_info = linea_info

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._linea_id, {}).get("estado", STATE_NORMAL)

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        linea_data = self.coordinator.data.get(self._linea_id, {})
        return {
            "detalle": linea_data.get("detalle", ""),
            "color": self._linea_info["color"],
        }

    @property
    def available(self):
        return self.coordinator.data is not None

    @property
    def device_info(self):
        return DEVICE_INFO


class SubteForecastSensor(CoordinatorEntity, SensorEntity):
    """Sensor de próximo tren en una dirección."""

    _attr_native_unit_of_measurement = "min"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_icon = "mdi:clock-outline"

    def __init__(
        self,
        coordinator: ForecastCoordinator,
        estacion: str,
        direction_id: int,
        direccion_label: str,
    ):
        super().__init__(coordinator)
        self._estacion = estacion
        self._direction_id = direction_id
        self._direccion_label = direccion_label  # "centro" o "cabecera"

        estacion_slug = estacion.lower().replace(" ", "_")
        self._attr_name = f"{estacion} → {direccion_label.capitalize()}"
        self._attr_unique_id = f"subte_ba_forecast_{estacion_slug}_{direccion_label}"

    def _get_proximo(self) -> dict | None:
        """Obtener el próximo tren en esta dirección."""
        if not self.coordinator.data:
            return None

        ahora = datetime.now().timestamp()
        candidatos = []

        for entity in self.coordinator.data:
            linea = entity.get("Linea", {})
            if linea.get("Direction_ID") != self._direction_id:
                continue

            route = linea.get("Route_Id", "")

            for est in linea.get("Estaciones", []):
                if est["stop_name"].lower() != self._estacion.lower():
                    continue

                arr_time = est["arrival"]["time"]
                minutos = round((arr_time - ahora) / 60)

                if minutos >= 0:
                    candidatos.append({
                        "linea": route,
                        "minutos": minutos,
                        "hora_llegada": datetime.fromtimestamp(arr_time).strftime("%H:%M"),
                    })

        if not candidatos:
            return None

        return min(candidatos, key=lambda x: x["minutos"])

    @property
    def native_value(self):
        proximo = self._get_proximo()
        return proximo["minutos"] if proximo else None

    @property
    def extra_state_attributes(self):
        proximo = self._get_proximo()
        if not proximo:
            return {}
        return {
            "linea": proximo["linea"],
            "hora_llegada": proximo["hora_llegada"],
        }

    @property
    def available(self):
        return self.coordinator.data is not None

    @property
    def device_info(self):
        return DEVICE_INFO
