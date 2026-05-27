# 🚇 Subte Buenos Aires — Home Assistant Integration

A Home Assistant integration that shows the **real-time status of Buenos Aires subway lines** using the [GCBA Transport API](https://api-transporte.buenosaires.gob.ar).

---

## Sensors

### Service Alerts (one per line)

| Sensor | Description |
|--------|-------------|
| `sensor.linea_a` | Línea A status |
| `sensor.linea_b` | Línea B status |
| `sensor.linea_c` | Línea C status |
| `sensor.linea_d` | Línea D status |
| `sensor.linea_e` | Línea E status |
| `sensor.linea_h` | Línea H status |
| `sensor.premetro` | Premetro status |

Each sensor returns `Normal` or the active alert description (e.g. `"Estación Malabia cerrada por obras de renovación integral."`).

### Next Train (optional, per station)

For each configured station, two sensors are created:

| Sensor | Description |
|--------|-------------|
| `sensor.<station>_centro` | Minutes until next train toward Centro |
| `sensor.<station>_cabecera` | Minutes until next train toward Cabecera |

Each sensor returns the number of minutes until arrival and includes two attributes: `linea` and `hora_llegada`.

Stations are selected from a full dropdown list during setup (e.g. `Línea A - Puán`). Multiple stations can be selected at once.

> **Note:** Next train sensors retain their last known value outside service hours instead of showing `unavailable`.

---

## Requirements

- Home Assistant 2023.1 or later
- [HACS](https://hacs.xyz) installed
- Credentials from the [GCBA Transport API](https://api-transporte.buenosaires.gob.ar) (free registration)

---

## Installation via HACS

1. In HACS, go to **Integrations → ⋮ → Custom repositories**
2. Add the URL of this repository
3. Select category **Integration**
4. Search for **"Subte Buenos Aires"** and install
5. Restart Home Assistant

---

## Configuration

1. Go to **Settings → Devices & Services → + Add Integration**
2. Search for **"Subte Buenos Aires"**
3. Fill in the form:

| Field | Description |
|-------|-------------|
| Client ID | From the GCBA API portal |
| Client Secret | From the GCBA API portal |
| Alerts update interval | How often to poll service alerts (default: 120s, min: 30s) |
| Next train update interval | How often to poll arrival forecasts (default: 30s, min: 30s) |
| Stations | Select one or more stations for next train sensors (optional) |

---

## Dashboard card example

```yaml
type: entities
title: 🚇 Subte Buenos Aires
entities:
  - entity: sensor.linea_a
    name: "🔵 Línea A"
  - entity: sensor.linea_b
    name: "🔴 Línea B"
  - entity: sensor.linea_c
    name: "🔵 Línea C"
  - entity: sensor.linea_d
    name: "🟢 Línea D"
  - entity: sensor.linea_e
    name: "🟣 Línea E"
  - entity: sensor.linea_h
    name: "🟡 Línea H"
  - entity: sensor.premetro
    name: "🟠 Premetro"
  - entity: sensor.puan_centro
    name: "Puán → Centro"
  - entity: sensor.puan_cabecera
    name: "Puán → Cabecera"
```
