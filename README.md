# FARO

Vigilante abierto de tarifas del ecosistema LLM.

Cada dia, FARO fotografia el catalogo completo de modelos y precios (400+ modelos de todos los proveedores relevantes), lo compara con el dia anterior y publica los cambios: subidas, bajadas, lanzamientos, retiradas y ampliaciones de contexto.

El historial completo vive en este repositorio. Cada snapshot es un commit. Nadie puede reconstruir este archivo hacia atras: solo se puede acumular hacia adelante, dia a dia.

## Salidas

- `ALERTAS.md`: resumen legible de la ultima vigilancia.
- `data/snapshots/`: catalogo completo fechado (precios USD por millon de tokens).
- `data/events/`: eventos detectados en formato JSON, listos para consumir por API.

## Ejecutar en local

```
python faro_watch.py
```

Test sin conexion (fixtures deterministas):

```
python faro_watch.py --mock
python faro_watch.py --mock
```

La primera ejecucion crea el snapshot base; la segunda detecta subidas, bajadas, un lanzamiento, una retirada y un cambio de contexto.

## Impacto personal

Copia `perfil.ejemplo.json` a `perfil.json`, declara tu consumo mensual estimado por modelo y FARO traducira cada cambio de tarifa a su efecto en tu factura.

## Alertas por Telegram

Define `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` como variables de entorno (o secrets del repositorio) y recibiras un resumen cuando haya movimientos.

Un proyecto de Strange Loop Factory.
