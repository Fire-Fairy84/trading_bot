# Trading Strategy Validation Lab

Repositorio para analizar y validar estrategias de trading con dos entornos de trabajo:

- `src/` para investigación y comparación rápida con `backtesting.py`
- `freqtrade-docker/` para validación operativa sobre `crypto spot` con `Freqtrade + Docker`

## Resumen

Este repositorio no presenta una estrategia lista para producción. Documenta un proceso de validación: definición de reglas, comparación de variantes, contraste entre `timeframes`, revisión de resultados y cierre con una conclusión explícita sobre límites y robustez.

La candidata más interesante en la validación con `Freqtrade` es `MiEstrategiaFaseB` en `4h`, pero la evidencia actual sigue siendo insuficiente para considerarla robusta.

## Enfoque

Este repositorio documenta un proceso de trabajo más que una estrategia final.

La idea principal es separar dos necesidades distintas:

1. `src/`: laboratorio de investigación sobre datasets reproducibles
2. `freqtrade-docker/`: entorno de validación operativa con configuración separada del core

La primera capa permite iterar sobre reglas, métricas y variantes con rapidez. La segunda permite comprobar una versión de esa línea de trabajo en un entorno más cercano a ejecución real, sin mezclar configuración local con el código de estrategia.

El objetivo de esta fase es mantener un proceso simple y defendible:

- comparar variantes con reglas simples y métricas consistentes
- evitar optimización oportunista
- documentar límites y riesgo de `overfitting`
- cerrar la validación con una conclusión defendible

## Qué se trabajó

La validación principal sobre `Freqtrade` se centra en dos estrategias long-only para `crypto spot`:

- `MiEstrategia`: versión base educativa, sencilla y fácil de depurar.
- `MiEstrategiaFaseB`: traducción simple de la lógica swing desarrollada en fases previas del proyecto.

Los criterios de esta fase han sido:

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

## Resultado principal

- `MiEstrategia`: `No consistente`
- `MiEstrategiaFaseB`: `Prometedora pero necesita más validación`
- lectura global del repositorio: `Interesante pero no robusta`

La mejor señal aparece en `MiEstrategiaFaseB` sobre `4h`, con mejor equilibrio entre retorno y drawdown que el resto de combinaciones observadas. Aun así, el comportamiento no se mantiene con la misma calidad en todos los `timeframes`, así que no hay base suficiente para una conclusión más fuerte.

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
│   ├── load_data.py
│   ├── strategy.py
│   ├── evaluation.py
│   └── run_backtest.py
├── specs/
└── tests/
```

## Arquitectura del proyecto

### `src/` y `tests/`: laboratorio cuantitativo

La carpeta `src/` contiene la parte más controlada del repositorio:

- descarga y carga de datos con `yfinance`
- estrategias y benchmarks en `backtesting.py`
- comparación `in-sample` / `out-of-sample`
- reportes y tests automatizados

Aquí está el trabajo de investigación: definición de reglas, comparación entre variantes y lectura de resultados.

### `freqtrade-docker/`: validación operativa sobre crypto

La carpeta `freqtrade-docker/` añade una capa de validación operativa:

- configuración separada del código base
- estrategias custom montadas en `user_data/strategies/`
- backtesting multi-par en `Binance spot`
- base preparada para `dry-run`

No sustituye al laboratorio de `src/`. Se usa para comprobar comportamiento, reproducibilidad y flujo de trabajo en un entorno distinto.

## Metodología de validación

Se usó el mismo protocolo para todos los backtests de `Freqtrade`:

- exchange: `Binance spot`
- pares: `BTC/USDT`, `ETH/USDT`, `BNB/USDT`, `SOL/USDT`, `XRP/USDT`
- `timerange`: `2024-04-01` a `2026-03-31`
- sin cambios de parámetros entre runs
- `max_open_trades = 1`
- `stake_amount = 100 USDT`

Notas metodológicas:

- `MiEstrategiaFaseB` necesita más velas de arranque (`startup_candle_count = 220`)
- para mantener una ventana efectiva comparable, el histórico se descargó con `--prepend`
- no se hizo optimización de parámetros entre comparativas

## Qué hace cada estrategia

### `MiEstrategia`

Estrategia base:

- usa `EMA 12/26`
- usa `RSI` como filtro de momentum
- toma beneficios con `minimal_roi`
- sale cuando la media rápida pierde fuerza o el `RSI` cae

Es fácil de seguir y sirve bien como referencia, pero depende bastante del `ROI` fijo y muestra sensibilidad al `timeframe`.

### `MiEstrategiaFaseB`

Versión más cercana a una lógica swing:

- filtro de tendencia con `SMA 50 > SMA 200`
- precio por encima de `SMA 50`
- entrada por recuperación de `RSI`
- salida por pérdida de tendencia o momentum

La lógica es más coherente como estrategia swing, pero no mantiene el mismo comportamiento en todos los `timeframes`; mejora en `4h` y pierde calidad en `1h`.

## Resultados resumidos

| Estrategia | Timeframe | Profit total | Trades | Win rate | Max drawdown | Profit factor |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `MiEstrategia` | `1h` | `8.34%` | `1330` | `62.3%` | `5.05%` | `1.08` |
| `MiEstrategia` | `4h` | `3.50%` | `594` | `78.3%` | `5.39%` | `1.07` |
| `MiEstrategia` | `6h` | `-3.77%` | `415` | `79.0%` | `5.71%` | `0.92` |
| `MiEstrategiaFaseB` | `1h` | `3.20%` | `390` | `21.8%` | `6.93%` | `1.08` |
| `MiEstrategiaFaseB` | `4h` | `9.26%` | `84` | `28.6%` | `2.49%` | `1.70` |
| `MiEstrategiaFaseB` | `6h` | `4.23%` | `59` | `27.1%` | `4.64%` | `1.34` |

Detalle adicional por par en `docs/freqtrade-validation.md`.

## Lectura honesta

### `MiEstrategia`

- Aguanta razonablemente en `1h` y `4h`, pero empeora en `6h`.
- Tiene `win rate` alto, pero la ventaja estadística es débil.
- `profit factor` cerca de `1.0` en todos los casos.
- No parece robusta: el rendimiento depende bastante del `timeframe`.

Conclusión: `No consistente`

### `MiEstrategiaFaseB`

- Se comporta mal o de forma mediocre en `1h`.
- Mejora claramente en `4h`.
- Sigue siendo positiva en `6h`, pero con menor consistencia entre pares.
- El mejor resultado aparece en un `timeframe` concreto, lo que obliga a desconfiar un poco.

Conclusión: `Prometedora pero necesita más validación`

## Riesgo de overfitting

Existe riesgo de `overfitting`, aunque no se hayan optimizado parámetros de forma agresiva.

Motivos:

- la mejora de `MiEstrategiaFaseB` se concentra sobre todo en `4h`
- en `1h` la misma idea pierde mucha calidad
- en `6h` mantiene resultado positivo, pero depende más de pocos trades y de algunos pares concretos
- la validación sigue limitada a un único exchange y un único universo pequeño de pares

La lectura razonable no es "funciona", sino:

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

No hay evidencia suficiente para considerar la estrategia apta para producción.

El valor del repositorio está en el proceso de validación:

- separación entre investigación y validación operativa
- entorno reproducible con `Freqtrade + Docker`
- separación entre configuración, estrategia y core
- comparación entre varios `timeframes`
- contraste entre varios pares
- documentación explícita de límites y resultados

La mejor candidata actual es `MiEstrategiaFaseB` en `4h`, pero necesita más validación antes de merecer cualquier confianza práctica.

## Siguiente paso prudente

El siguiente paso razonable, sin cambiar parámetros, sería:

- `forward test` corto en `dry-run`
- mismo conjunto de pares
- mismo `timeframe` (`4h`)
- sin tocar parámetros

Eso serviría para comprobar estabilidad operativa, no para justificar uso en `live`.

## Ejecución

Para la parte de `Freqtrade`, los comandos principales están documentados en `freqtrade-docker/README.md`.

Resumen rápido:

```bash
cp .env.example .env
docker compose up -d freqtrade
docker compose run --rm freqtrade download-data --prepend --config /freqtrade/user_data/config.validation.json --timeframe 4h --timerange 20240101-20260331
docker compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.validation.json --strategy MiEstrategiaFaseB --timeframe 4h --timerange 20240401-20260331
```
