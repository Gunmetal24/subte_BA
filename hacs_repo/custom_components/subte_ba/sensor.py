"""Sensores para Subte Buenos Aires."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LINEAS, STATE_NORMAL
from .coordinator import SubteCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Crear sensores a partir de una config entry."""
    coordinator: SubteCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SubteSensor(coordinator, linea_id, linea_info)
        for linea_id, linea_info in LINEAS.items()
    ]
    async_add_entities(entities)


class SubteSensor(CoordinatorEntity, SensorEntity):
    """Sensor de estado para una línea de subte."""

    def __init__(
        self,
        coordinator: SubteCoordinator,
        linea_id: str,
        linea_info: dict,
    ) -> None:
        """Inicializar el sensor."""
        super().__init__(coordinator)
        self._linea_id = linea_id
        self._linea_info = linea_info
        self._attr_name = linea_info["nombre"]
        self._attr_unique_id = f"subte_ba_{linea_id.lower()}"
        self._attr_icon = linea_info["icon"]

    @property
    def native_value(self) -> str:
        """Estado actual de la línea."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._linea_id, {}).get("estado", STATE_NORMAL)

    @property
    def extra_state_attributes(self) -> dict:
        """Atributos extra del sensor."""
        if self.coordinator.data is None:
            return {}
        linea_data = self.coordinator.data.get(self._linea_id, {})
        return {
            "detalle": linea_data.get("detalle", ""),
            "color": self._linea_info["color"],
            "linea_id": self._linea_id,
        }

    @property
    def available(self) -> bool:
        """El sensor está disponible si el coordinator tiene datos."""
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        """Agrupar todos los sensores bajo un único dispositivo."""
        return {
            "identifiers": {(DOMAIN, "subte_ba")},
            "name": "Subte Buenos Aires",
            "manufacturer": "GCBA / Emova",
            "model": "API Transporte GCBA",
            "entry_type": "service",
        }
