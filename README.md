# 🚇 Subte Buenos Aires — Home Assistant Integration

Integración para Home Assistant que muestra el **estado en tiempo real de las líneas de subte de Buenos Aires** usando la [API de Transporte del GCBA](https://buenosaires.gob.ar/desarrollourbano/transporte/apitransporte).

## Novedades v1.0.3
- Ante errores 500 intermitentes de la API, los sensores mantienen el **último valor conocido** en lugar de quedar unavailable.
- Tolerancia de hasta 3 errores consecutivos antes de marcar unavailable.

## Instalación via HACS
1. HACS → Integraciones → ⋮ → Repositorios personalizados
2. URL: `https://github.com/Gunmetal24/subte_BA` | Categoría: Integración
3. Instalar y reiniciar HA
4. Configuración → Dispositivos y servicios → + Agregar integración → Subte Buenos Aires
