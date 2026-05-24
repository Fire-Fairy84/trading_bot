# Freqtrade Validation Notes

## Setup

- exchange: `Binance spot`
- pairs: `BTC/USDT`, `ETH/USDT`, `BNB/USDT`, `SOL/USDT`, `XRP/USDT`
- requested timerange: `2024-04-01` to `2026-03-31`
- config: [`config.validation.json`](../freqtrade-docker/user_data/config.validation.json)

## Compact Methodology Summary

| Field | Value |
| --- | --- |
| dataset | `Binance spot` with `BTC/USDT`, `ETH/USDT`, `BNB/USDT`, `SOL/USDT`, `XRP/USDT` |
| period | `2024-04-01` to `2026-03-31` |
| costs and conditions | `stake_amount = 100 USDT`, `max_open_trades = 1`, same parameters across all runs |
| comparison criteria | same validation protocol for both strategies; comparison by `timeframe`, `profit total`, `trades`, `win rate`, `max drawdown`, and `profit factor` |
| main conclusion | `MiEstrategiaFaseB` in `4h` is the strongest current candidate, but the project remains `Interesante pero no robusta` |

## Main Limits

- single exchange
- small pair universe
- clear `timeframe` sensitivity
- `overfitting` risk even without aggressive parameter optimization

## Metrics Summary

| Strategy | Timeframe | Profit total | Trades | Win rate | Max drawdown | Profit factor |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `MiEstrategia` | `1h` | `8.34%` | `1330` | `62.3%` | `5.05%` | `1.08` |
| `MiEstrategia` | `4h` | `3.50%` | `594` | `78.3%` | `5.39%` | `1.07` |
| `MiEstrategia` | `6h` | `-3.77%` | `415` | `79.0%` | `5.71%` | `0.92` |
| `MiEstrategiaFaseB` | `1h` | `3.20%` | `390` | `21.8%` | `6.93%` | `1.08` |
| `MiEstrategiaFaseB` | `4h` | `9.26%` | `84` | `28.6%` | `2.49%` | `1.70` |
| `MiEstrategiaFaseB` | `6h` | `4.23%` | `59` | `27.1%` | `4.64%` | `1.34` |

## Pair-Level Notes

### `MiEstrategia`

- `1h`: 4 de 5 pares en positivo. Mejor par `SOL/USDT` (`4.25%`). Peor par `XRP/USDT` (`-0.13%`).
- `4h`: 4 de 5 pares en positivo. Mejor par `ETH/USDT` (`2.04%`). Peor par `XRP/USDT` (`-1.25%`).
- `6h`: 1 de 5 pares en positivo de forma marginal. Mejor par `SOL/USDT` (`0.06%`). Peor par `BTC/USDT` (`-2.60%`).

### `MiEstrategiaFaseB`

- `1h`: 1 de 5 pares en positivo claro. Mejor par `XRP/USDT` (`13.45%`). Peor par `BNB/USDT` (`-3.16%`).
- `4h`: 5 de 5 pares en positivo. Mejor par `BNB/USDT` (`3.06%`). Peor par `ETH/USDT` (`0.88%`).
- `6h`: 2 de 5 pares en positivo. Mejor par `XRP/USDT` (`4.94%`). Peor par `BNB/USDT` (`-2.56%`).

## Interpretation

- `MiEstrategia` no es robusta. Gana algo en `1h` y `4h`, pero se rompe en `6h`.
- `MiEstrategiaFaseB` es la candidata interesante. `4h` destaca con la mejor combinacion de retorno y drawdown.
- La misma estrategia no es estable en `1h`, lo que obliga a evitar cualquier conclusion triunfalista.
- Hay riesgo de `overfitting` por dependencia de `timeframe` y de algunos pares concretos.

## Final Assessment

- `MiEstrategia`: `No consistente`
- `MiEstrategiaFaseB`: `Prometedora pero necesita más validación`
- Proyecto: `Interesante pero no robusta`
