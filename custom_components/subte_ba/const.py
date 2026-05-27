"""Constantes para la integración Subte Buenos Aires."""

DOMAIN = "subte_ba"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_SCAN_INTERVAL_ALERTS = "scan_interval_alerts"
CONF_SCAN_INTERVAL_FORECAST = "scan_interval_forecast"
CONF_ESTACION = "estacion"

DEFAULT_SCAN_INTERVAL_ALERTS = 120
DEFAULT_SCAN_INTERVAL_FORECAST = 30
MIN_SCAN_INTERVAL = 30
MAX_SCAN_INTERVAL = 3600

API_BASE = "https://apitransporte.buenosaires.gob.ar/subtes"
API_ALERTS = f"{API_BASE}/serviceAlerts"
API_FORECAST = f"{API_BASE}/forecastGTFS"

LINEAS = {
    "LineaA": {"nombre": "Línea A", "color": "#18ADEF", "icon": "mdi:subway"},
    "LineaB": {"nombre": "Línea B", "color": "#EC1C24", "icon": "mdi:subway"},
    "LineaC": {"nombre": "Línea C", "color": "#005EB8", "icon": "mdi:subway"},
    "LineaD": {"nombre": "Línea D", "color": "#00A550", "icon": "mdi:subway"},
    "LineaE": {"nombre": "Línea E", "color": "#8B4513", "icon": "mdi:subway"},
    "LineaH": {"nombre": "Línea H", "color": "#FFD700", "icon": "mdi:subway"},
    "Premetro": {"nombre": "Premetro", "color": "#FF8C00", "icon": "mdi:tram"},
}

STATE_NORMAL = "Normal"

DIRECTION_CENTRO = 1
DIRECTION_CABECERA = 0

# Estaciones por línea en orden cabecera oeste → cabecera este
ESTACIONES_POR_LINEA: dict[str, list[str]] = {
    "LineaA": [
        "San Pedrito", "San José de Flores", "Carabobo", "Puán",
        "Primera Junta", "Acoyte", "Río de Janeiro", "Castro Barros",
        "Loria", "Plaza Miserere", "Alberti", "Pasco", "Congreso",
        "Sáenz Peña", "Lima", "Piedras", "Perú", "Plaza de Mayo",
    ],
    "LineaB": [
        "Juan Manuel de Rosas", "Echeverría", "De Los Incas - Parque Chas",
        "Tronador - Villa Ortúzar", "Federico Lacroze", "Dorrego",
        "Ángel Gallardo", "Malabia", "Medrano", "Carlos Gardel",
        "Pueyrredón", "Pasteur", "Callao", "Uruguay",
        "Carlos Pelegrini", "Florida", "Leandro N. Alem",
    ],
    "LineaC": [
        "Constitución", "San Juan", "Independencia", "Moreno",
        "Av. de Mayo", "Diagonal Norte", "Lavalle", "General San Martín",
        "Retiro",
    ],
    "LineaD": [
        "Congreso de Tucumán", "Juramento", "José Hernández", "Olleros",
        "Ministro Carranza", "Palermo", "Plaza Italia", "Scalabrini Ortíz",
        "Bulnes", "Agüero", "Pueyrredón", "Facultad de Medicina",
        "Callao", "Tribunales", "9 de Julio", "Catedral",
    ],
    "LineaE": [
        "Plaza de los Virreyes", "Varela", "Medalla Milagrosa",
        "Emilio Mitre", "Moreno", "Av. La Plata", "Boedo",
        "General Urquiza", "Jujuy", "Pichincha", "Entre Ríos",
        "San José", "Independencia", "Belgrano", "Bolivar",
        "Correo Central", "Catalinas", "Retiro",
    ],
    "LineaH": [
        "Hospitales", "Inclán", "Humberto I", "Venezuela",
        "Once", "Corrientes", "Las Heras", "Santa Fe", "Córdoba",
    ],
    "Premetro": [
        "General Savio", "Cementerio", "Larrazábal", "Atlético Lugano",
        "Escalada", "Penal de Devoto", "Eva Perón",
    ],
}

# Lista de opciones para el selector del config flow: "Línea X - Estación" → "stop_name"
ESTACIONES_SELECTOR: dict[str, str] = {}
for _linea_id, _estaciones in ESTACIONES_POR_LINEA.items():
    _letra = _linea_id.replace("Linea", "Línea ")
    for _est in _estaciones:
        _key = f"{_letra} - {_est}"
        ESTACIONES_SELECTOR[_key] = _est
