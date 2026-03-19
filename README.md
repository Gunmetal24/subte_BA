# 🚇 Subte Buenos Aires — Home Assistant Integration

Integración para Home Assistant que muestra el **estado en tiempo real de las líneas de subte de Buenos Aires** usando la [API de Transporte del GCBA](https://buenosaires.gob.ar/desarrollourbano/transporte/apitransporte).

## Sensores incluidos

| Sensor | Descripción |
|--------|-------------|
| `sensor.linea_a` | Estado Línea A |
| `sensor.linea_b` | Estado Línea B |
| `sensor.linea_c` | Estado Línea C |
| `sensor.linea_d` | Estado Línea D |
| `sensor.linea_e` | Estado Línea E |
| `sensor.linea_h` | Estado Línea H |
| `sensor.premetro` | Estado Premetro |

Cada sensor devuelve `Normal` o la descripción de la alerta activa (ej: `"Estación Malabia cerrada por obras de renovación integral."`).

## Requisitos

- Home Assistant 2023.1 o superior
- [HACS](https://hacs.xyz) instalado
- Credenciales de la [API de Transporte del GCBA](https://buenosaires.gob.ar/desarrollourbano/transporte/apitransporte) (registro gratuito)

## Instalación via HACS

1. En HACS, ir a **Integraciones → ⋮ → Repositorios personalizados**
2. Agregar la URL de este repositorio
3. Seleccionar categoría **Integración**
4. Buscar **"Subte Buenos Aires"** e instalar
5. Reiniciar Home Assistant

## Configuración

1. Ir a **Configuración → Dispositivos y servicios → + Agregar integración**
2. Buscar **"Subte Buenos Aires"**
3. Ingresar tu `Client ID` y `Client Secret` de la API del GCBA
4. ¡Listo!

## Tarjeta de ejemplo para el dashboard

```yaml
type: entities
title: 🚇 Estado del Subte
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
```

## Créditos

Datos provistos por la [API de Transporte del GCBA](https://buenosaires.gob.ar/desarrollourbano/transporte/apitransporte).
