# Forward Test Checklist

Checklist corto para una validación final en `dry-run`, sin tocar parámetros.

## Configuración fija

- estrategia: `MiEstrategiaFaseB`
- timeframe: `4h`
- pares: `BTC/USDT`, `ETH/USDT`, `BNB/USDT`, `SOL/USDT`, `XRP/USDT`
- modo: `dry_run`
- sin optimización de parámetros

## Arranque

```bash
cd /Users/esther/Proyectos/trading-bot/freqtrade-docker
docker compose up -d freqtrade
docker compose logs -f freqtrade
```

## Qué revisar 2–3 veces al día

- el bot arranca sin errores
- la estrategia cargada es `MiEstrategiaFaseB`
- el `timeframe` activo es `4h`
- sigue en `dry_run`
- no hay errores de datos, exchange o permisos
- aparecen señales razonables
- la actividad no depende por completo de un único par
- las salidas parecen coherentes con una lógica swing

## Qué anotar

- número de señales
- número de trades simulados abiertos y cerrados
- pares más activos
- errores operativos, si aparecen
- cualquier comportamiento que contradiga claramente el backtesting

## Señales de alerta

- no genera señales en absoluto
- casi toda la actividad recae en un solo par
- abre y cierra demasiado rápido para una lógica `4h`
- hay errores repetidos en logs
- el comportamiento observado contradice de forma clara la hipótesis del backtest

## Criterio de cierre

El objetivo de este `forward test` no es aprobar la estrategia para `live`, sino decidir si la etiqueta final del proyecto debe mantenerse como:

- `Interesante pero no robusta`
- `Prometedora pero necesita más validación`
- `No consistente`
