# Trading Bot Validation Project

Proyecto educativo de trading algorítmico orientado a portfolio. El foco no es vender una estrategia "ganadora", sino mostrar un proceso creíble de validación con `Freqtrade`, `Docker` y criterios cuantitativos básicos.

## Objetivo

Validar de forma honesta dos estrategias long-only sobre `crypto spot`:

- `MiEstrategia`: versión base educativa, sencilla y fácil de depurar.
- `MiEstrategiaFaseB`: traducción simple de la lógica swing desarrollada en fases previas del proyecto.

La prioridad de esta fase ha sido:

- no optimizar parámetros
- mantener condiciones consistentes entre runs
- comparar varios `timeframes`
- comparar varios pares líquidos
- documentar resultados sin hype

## Stack

- `Python`
- `Docker`
- `Docker Compose`
- `Freqtrade`
- `Binance spot`

## Estructura

```text
trading-bot/
├── README.md
├── docs/
│   └── freqtrade-validation.md
├── freqtrade-docker/
│   ├── docker-compose.yml
│   ├── README.md
│   └── user_data/
│       ├── config.json
│       ├── config.validation.json
│       └── strategies/
│           └── my_strategy.py
├── src/
├── specs/
└── tests/
```

## Qué hace cada estrategia

### `MiEstrategia`

Estrategia base de aprendizaje:

- usa `EMA 12/26`
- usa `RSI` como filtro de momentum
- toma beneficios con `minimal_roi`
- sale cuando la media rápida pierde fuerza o el `RSI` cae

Ventaja: muy fácil de entender.

Riesgo: depende bastante del `ROI` fijo y muestra sensibilidad al `timeframe`.

### `MiEstrategiaFaseB`

Versión más cercana a una lógica swing:

- filtro de tendencia con `SMA 50 > SMA 200`
- precio por encima de `SMA 50`
- entrada por recuperación de `RSI`
- salida por pérdida de tendencia o momentum

Ventaja: conceptualmente más coherente como estrategia swing.

Riesgo: no es estable en todos los `timeframes`; mejora mucho en `4h`, pero no mantiene la misma calidad en `1h`.

## Protocolo de validación

Se usó el mismo protocolo para todos los runs:

- exchange: `Binance spot`
- pares: `BTC/USDT`, `ETH/USDT`, `BNB/USDT`, `SOL/USDT`, `XRP/USDT`
- `timerange`: `2024-04-01` a `2026-03-31`
- sin cambios de parámetros entre runs
- `max_open_trades = 1`
- `stake_amount = 100 USDT`

Nota metodológica:

- `MiEstrategiaFaseB` necesita más velas de arranque (`startup_candle_count = 220`).
- Para que la ventana efectiva fuese comparable, se descargó histórico previo con `--prepend`.

## Resultados resumidos

| Estrategia | Timeframe | Profit total | Trades | Win rate | Max drawdown | Profit factor |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `MiEstrategia` | `1h` | `8.34%` | `1330` | `62.3%` | `5.05%` | `1.08` |
| `MiEstrategia` | `4h` | `3.50%` | `594` | `78.3%` | `5.39%` | `1.07` |
| `MiEstrategia` | `6h` | `-3.77%` | `415` | `79.0%` | `5.71%` | `0.92` |
| `MiEstrategiaFaseB` | `1h` | `3.20%` | `390` | `21.8%` | `6.93%` | `1.08` |
| `MiEstrategiaFaseB` | `4h` | `9.26%` | `84` | `28.6%` | `2.49%` | `1.70` |
| `MiEstrategiaFaseB` | `6h` | `4.23%` | `59` | `27.1%` | `4.64%` | `1.34` |

## Lectura honesta

### `MiEstrategia`

- Aguanta razonablemente en `1h` y `4h`, pero empeora en `6h`.
- Tiene `win rate` alto, pero la ventaja estadística es débil.
- `profit factor` cerca de `1.0` en todos los casos.
- No parece robusta: el rendimiento depende bastante del `timeframe`.

Decisión:

- `No consistente`

### `MiEstrategiaFaseB`

- Se comporta mal o de forma mediocre en `1h`.
- Mejora claramente en `4h`.
- Sigue siendo positiva en `6h`, pero con menor consistencia entre pares.
- El mejor resultado aparece en un `timeframe` concreto, lo que obliga a desconfiar un poco.

Decisión:

- `Prometedora pero necesita más validación`

## Riesgo de overfitting

Sí, existe riesgo de `overfitting`, aunque no se hayan optimizado parámetros de forma agresiva.

Motivos:

- la mejora de `MiEstrategiaFaseB` se concentra sobre todo en `4h`
- en `1h` la misma idea pierde mucha calidad
- en `6h` mantiene resultado positivo, pero depende más de pocos trades y de algunos pares concretos
- la validación sigue limitada a un único exchange y un único universo pequeño de pares

La conclusión razonable no es "funciona", sino:

- hay una hipótesis de trabajo interesante en `4h`
- todavía no hay evidencia suficiente para llamarla robusta

## Cómo ejecutar Freqtrade

Desde [freqtrade-docker](/Users/esther/Proyectos/trading-bot/freqtrade-docker):

```bash
cp .env.example .env
docker compose up -d freqtrade
docker compose logs -f freqtrade
```

Descarga de datos de validación:

```bash
docker compose run --rm freqtrade download-data --prepend --config /freqtrade/user_data/config.validation.json --timeframe 4h --timerange 20240101-20260331
```

Backtesting de la estrategia base:

```bash
docker compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.validation.json --strategy MiEstrategia --timeframe 4h --timerange 20240401-20260331
```

Backtesting de la variante swing:

```bash
docker compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.validation.json --strategy MiEstrategiaFaseB --timeframe 4h --timerange 20240401-20260331
```

## Conclusión final

Este proyecto no demuestra una estrategia lista para producción.

Sí demuestra algo más útil para portfolio junior:

- que sabes montar un entorno reproducible con `Freqtrade + Docker`
- que sabes separar configuración, estrategia y core
- que sabes validar en varios `timeframes`
- que sabes contrastar varios pares
- que sabes cerrar una conclusión honesta aunque el resultado no sea espectacular

Conclusión final del proyecto:

- `Interesante pero no robusta`

La mejor candidata actual es `MiEstrategiaFaseB` en `4h`, pero necesita más validación antes de merecer cualquier confianza práctica.

## Siguiente paso prudente

Si se quisiera estirar un poco más la validación sin caer en optimización oportunista, el siguiente paso razonable sería:

- `forward test` corto en `dry-run`
- mismo conjunto de pares
- mismo `timeframe` (`4h`)
- sin tocar parámetros

Eso serviría para comprobar estabilidad operativa, no para declarar la estrategia apta para `live`.
