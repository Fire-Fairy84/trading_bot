# Proyecto Trading

Proyecto educativo para aprender trading algorítmico con Python paso a paso, usando `backtesting.py` como base de validación.

## Objetivo

Construir una base técnica simple, entendible y reproducible para:

- descargar y preparar datos OHLCV
- implementar una estrategia swing long-only
- aplicar gestión de riesgo básica
- comparar variantes de la estrategia
- validar resultados con separación temporal `in-sample` / `out-of-sample`
- generar reportes para revisar los resultados con calma

## Estado actual

El proyecto ya cubre:

- Fase A: entorno inicial, estructura del proyecto, carga de datos y primer backtest base
- Fase B: estrategia swing simple con indicadores, sizing por riesgo, stops, variantes y validación comparativa

Pendiente para la siguiente etapa:

- Fase C: portar la lógica a un entorno más cercano a producción, previsiblemente con Freqtrade + Docker

## Qué incluye ahora mismo

### Datos y carga

- descarga de datos OHLCV con `yfinance`
- carga desde CSV local para no depender siempre de red
- validación mínima de columnas y formato

### Estrategias e indicadores

- `BuyAndHoldStrategy` como benchmark básico
- `SmaCrossBenchmarkStrategy` como benchmark técnico simple
- `RiskManagedSwingStrategy` como estrategia principal de fase B

La estrategia principal usa:

- filtro de tendencia con `SMA 50 > SMA 200`
- señal de recuperación de momentum con `RSI`
- salida por pérdida de tendencia y/o momentum
- `stop loss` configurable
- tamaño de posición basado en riesgo por operación

### Variantes comparables

Se han añadido variantes para aprendizaje y comparación:

- `swing_risk_managed`: versión base
- `swing_flexible_entry`: entrada menos estricta
- `swing_calmer_exit`: salida menos agresiva y trailing stop
- `swing_wider_atr_stop`: stop ATR más amplio
- `swing_percent_stop`: variante opcional con stop porcentual fijo

### Evaluación

- extracción de métricas homogéneas para todas las estrategias
- partición temporal `in-sample` / `out-of-sample`
- comparación de varias estrategias sobre el mismo dataset
- resumen interpretativo para detectar la variante más prometedora

### Reportes

Al ejecutar el runner principal se generan:

- resumen CSV
- resumen Markdown
- reportes HTML por estrategia y por tramo temporal

## Estructura actual

```text
trading-bot/
├── README.md
├── requirements.txt
├── data/
│   └── SPY_1d.csv
├── reports/
├── specs/
├── src/
│   ├── evaluation.py
│   ├── load_data.py
│   ├── run_backtest.py
│   └── strategy.py
└── tests/
    ├── conftest.py
    ├── test_evaluation.py
    ├── test_indicators.py
    └── test_risk_management.py
```

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Importante: ejecuta siempre `source .venv/bin/activate` desde la raíz del repositorio antes de lanzar `python`, `pytest` o scripts del proyecto. En este repo asumimos ese entorno virtual local como contexto de trabajo.

## Uso

### Ejecutar el backtest principal

```bash
python src/run_backtest.py
```

Esto:

- carga `data/SPY_1d.csv` si ya existe
- descarga datos solo si el CSV no está disponible
- ejecuta la comparativa principal de variantes swing
- guarda resultados en `reports/`

### Ejecutar tests

```bash
pytest
```

## Métricas que estamos observando

Las comparativas actuales ponen el foco en:

- `return_pct`
- `buy_hold_return_pct`
- `vs_buy_hold_pct`
- `max_drawdown_pct`
- `sharpe_ratio`
- `trades`
- `win_rate_pct`
- `profit_factor`

La prioridad no es encontrar una estrategia "ganadora" todavía, sino aprender a validar mejor una idea y evitar conclusiones engañosas.

## Criterio de trabajo en esta fase

La filosofía del proyecto hasta fase B es:

- mantener la estrategia simple y explicable
- no optimizar demasiados parámetros a la vez
- comparar cambios pequeños y aislados
- dar más peso al resultado `out-of-sample` que al `in-sample`
- tratar el benchmark como referencia, no como enemigo

## Siguiente paso recomendado

La fase B queda cerrada con esta decisión de trabajo:

- variante candidata para promoción a fase C: `swing_calmer_exit`
- alternativa secundaria: `swing_wider_atr_stop`
- variante descartada por ahora como candidata principal: `swing_flexible_entry`

Motivo resumido:

- `swing_calmer_exit` ofrece el mejor equilibrio actual entre retorno, calidad de salida y comportamiento `out-of-sample`
- `swing_wider_atr_stop` también se comporta bien, pero prioriza más la contención de drawdown que la captura de movimiento
- `swing_flexible_entry` empeora de forma clara fuera de muestra y no merece promoción en esta etapa

La lectura metodológica es simple: para este proyecto, la hipótesis "salir menos agresivamente" queda mejor respaldada que la hipótesis "entrar antes".

## Cierre de Fase B

La decisión de promoción se basa en los resultados actuales sobre `SPY 1d` con separación temporal `70/30`:

- `swing_risk_managed`: `8.00%` out-of-sample, `-2.11%` max drawdown
- `swing_calmer_exit`: `7.43%` out-of-sample, `-2.27%` max drawdown
- `swing_wider_atr_stop`: `5.97%` out-of-sample, `-1.72%` max drawdown
- `swing_flexible_entry`: `-2.06%` out-of-sample, `-4.66%` max drawdown

Aunque la versión base obtiene un retorno ligeramente superior, `swing_calmer_exit` se selecciona como candidata principal porque la mejora conceptual es más clara y portable: reduce salidas demasiado nerviosas, deja respirar la posición y mantiene un perfil de riesgo cercano al de la estrategia original.

Este cierre no pretende demostrar robustez definitiva. La evidencia sigue limitada a:

- un activo principal (`SPY`)
- un timeframe (`1d`)
- una única partición temporal (`70/30`)

Por eso la promoción a fase C debe interpretarse como una decisión práctica de continuidad, no como una validación final de ventaja estructural.

Resumen práctico: la fase B ya no es una simple maqueta. Queda una candidata clara para portar a Freqtrade y una base suficientemente sólida para continuar aprendiendo en una fase más operativa.
