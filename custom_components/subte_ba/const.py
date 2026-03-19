"""Constantes para la integración Subte Buenos Aires."""

DOMAIN = "subte_ba"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"

DEFAULT_SCAN_INTERVAL = 120  # segundos
MIN_SCAN_INTERVAL = 30
MAX_SCAN_INTERVAL = 3600
CONF_SCAN_INTERVAL = "scan_interval"

API_BASE = "https://apitransporte.buenosaires.gob.ar/subtes"
API_ALERTS = f"{API_BASE}/serviceAlerts"

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
STATE_ERROR = "Error"
