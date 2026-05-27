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

    # Compatibilidad: puede ser lista (v1.0.7+) o string (versiones anteriores)
    estaciones_raw = entry.data.get(CONF_ESTACION, [])
    if isinstance(estaciones_raw, str):
        estaciones = [estaciones_raw] if estaciones_raw else []
    else:
        estaciones = estaciones_raw or []

    entities: list = [
        SubteAlertSensor(alerts_coord, linea_id, linea_info)
        for linea_id, linea_info in LINEAS.items()
    ]

    for estacion in estaciones:
        if estacion:
            entities.append(SubteForecastSensor(forecast_coord, estacion, DIRECTION_CENTRO, "Centro"))
            entities.append(SubteForecastSensor(forecast_coord, estacion, DIRECTION_CABECERA, "Cabecera"))

    async_add_entities(entities)


class SubteAlertSensor(CoordinatorEntity, SensorEntity):
    """Sensor de alertas por línea."""

    def __init__(self, coordinator: AlertsCoordinator, linea_id: str, linea_info: dict):
        super().__init__(coordinator)
        self._linea_id = linea_id
        self._linea_info = linea_info
        self._attr_name = linea_info["nombre"]
        self._attr_unique_id = f"subte_ba_{linea_id.lower()}"
        self._attr_icon = linea_info["icon"]

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
    """Sensor de próximo tren. Mantiene último valor conocido fuera de horario."""

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
        self._direccion_label = direccion_label

        estacion_slug = estacion.lower().replace(" ", "_")
        self._attr_name = f"{estacion} → {direccion_label}"
        self._attr_unique_id = f"subte_ba_forecast_{estacion_slug}_{direccion_label.lower()}"

        # Último valor conocido
        self._last_value: int | None = None
        self._last_attrs: dict = {}

    def _get_proximo(self) -> dict | None:
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
        if proximo is not None:
            self._last_value = proximo["minutos"]
            return proximo["minutos"]
        return self._last_value

    @property
    def extra_state_attributes(self):
        proximo = self._get_proximo()
        if proximo is not None:
            self._last_attrs = {
                "linea": proximo["linea"],
                "hora_llegada": proximo["hora_llegada"],
            }
        return self._last_attrs

    @property
    def available(self):
        return self.coordinator.data is not None

    @property
    def device_info(self):
        return DEVICE_INFO
