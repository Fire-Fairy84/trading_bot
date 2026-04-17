# Strategy Spec

## Objective

El objetivo de esta estrategia es validar si una lógica swing long-only, basada en tendencia de medio plazo y confirmación de momentum, puede ofrecer un equilibrio razonable entre retorno, drawdown y estabilidad operativa frente a benchmarks simples.

La finalidad de esta fase no es demostrar una ventaja estructural definitiva de mercado, sino comprobar si la combinación de filtro de tendencia, confirmación de entrada y gestión de riesgo produce un comportamiento más disciplinado que alternativas triviales.

## Market & Data

- Activo principal de referencia: `SPY`
- Tipo de activo: ETF de renta variable estadounidense
- Timeframe: diario (`1d`)
- Estructura de datos: OHLCV (`Open`, `High`, `Low`, `Close`, `Volume`)
- Universo actual: una única serie temporal usada como base educativa y de validación inicial

Este marco es adecuado para una estrategia swing porque reduce ruido intradía, facilita la interpretación de señales y permite centrar el aprendizaje en lógica de estrategia y evaluación.

## Entry Rules

La entrada long se produce únicamente cuando se cumple el conjunto completo de condiciones siguientes:

1. La tendencia principal es alcista, definida como `SMA 50 > SMA 200`.
2. El precio de cierre está por encima de la media rápida, lo que evita comprar activos claramente debilitados dentro de una tendencia ambigua.
3. El `RSI` confirma recuperación de momentum mediante un cruce alcista sobre el nivel de entrada definido para la variante activa.
4. Existe un `stop loss` válido y calculable.
5. El tamaño de posición resultante es compatible con el presupuesto de riesgo y con el capital disponible.

La lógica de entrada busca capturar continuidad alcista cuando el mercado ya muestra una estructura favorable, pero evitando una persecución tardía del precio.

## Exit Rules

La salida de la posición puede producirse por cualquiera de las siguientes causas:

1. El precio de cierre cae por debajo de la media rápida (`price < SMA 50`), lo que actúa como señal táctica de pérdida de fortaleza.
2. El `RSI` cae por debajo del umbral de salida definido, cuando la configuración de la variante activa utiliza una salida basada en `RSI`.
3. Activación del `stop loss`, ya sea en formato `ATR-based stop` o `percent stop`.
4. En variantes concretas, activación de un `trailing stop` para proteger beneficios sin cerrar de forma prematura por ruido menor.

La filosofía de salida combina defensa de capital con disciplina táctica. No intenta capturar la totalidad del movimiento, sino cerrar la posición cuando la hipótesis operativa deja de estar suficientemente respaldada.

## Risk Management

### Riesgo por operación

- Riesgo máximo objetivo: `1%` del equity por operación

Este criterio define una pérdida monetaria máxima tolerable antes de abrir la posición. El riesgo se calcula en función de la distancia entre el precio estimado de entrada y el nivel de stop.

### Stop Loss

La estrategia soporta dos enfoques principales:

- `ATR stop`: stop dinámico basado en volatilidad, usando un múltiplo del `Average True Range`
- `Percent stop`: stop fijo porcentual respecto al precio de entrada

El enfoque basado en `ATR` es el preferido en la validación principal porque adapta la distancia del stop al régimen de volatilidad del mercado.

### Position Sizing

El `position sizing` se calcula a partir de:

- equity disponible
- riesgo monetario permitido por operación
- distancia entre entrada y stop
- restricción adicional de asequibilidad real con el capital actual

Esto evita asignar un tamaño excesivo cuando el stop es muy estrecho o cuando el capital no permite sostener la posición sin asumir un apalancamiento implícito no deseado.

## Constraints

- Solo se permite una posición abierta a la vez.
- No se acumulan entradas simultáneas sobre la misma señal.
- No se duplican órdenes mientras exista una posición abierta.
- La señal debe estar confirmada con barras ya cerradas, reduciendo el riesgo de `look-ahead bias`.
- La estrategia es long-only en esta fase.

Estas restricciones simplifican la interpretación del sistema y favorecen una evaluación más limpia y reproducible.

## Benchmarks

La estrategia se compara contra dos referencias deliberadamente simples:

### Buy & Hold

Benchmark pasivo que representa la exposición continua al activo sin lógica táctica.

### SMA Crossover

Benchmark técnico simple basado en cruce de medias, útil para contrastar si la estrategia swing aporta algo más que una lógica muy básica de seguimiento de tendencia.

En la implementación actual, la comparación cuantificada explícita dentro de las métricas extraídas se realiza frente a `Buy & Hold`. El benchmark `SMA Crossover` se usa como referencia adicional de contexto y comparación entre estrategias, pero todavía no dispone de una métrica derivada específica equivalente a `vs_buy_hold_pct`.

## Evaluation Criteria

La evaluación se centra en métricas que permitan analizar retorno, riesgo y calidad operativa:

- `Return`
- `Buy & Hold Return`
- retorno relativo frente a `Buy & Hold`
- `Max Drawdown`
- `Sharpe Ratio`
- número de operaciones
- `Win Rate`
- `Profit Factor`

Ninguna métrica debe interpretarse de forma aislada. Un mayor retorno no implica una mejora real si viene acompañado de un aumento desproporcionado de drawdown, inestabilidad o dependencia excesiva de pocos trades.

### Importancia de Out-of-Sample

La validación `out-of-sample` es el criterio central de esta fase.

El tramo `in-sample` se utiliza para entender la estrategia, depurar la lógica y comparar variantes de forma controlada. El tramo `out-of-sample` se utiliza para comprobar si la idea mantiene un comportamiento razonable fuera del periodo empleado para diseñarla o ajustarla.

En consecuencia:

- una mejora solo en `in-sample` no debe considerarse evidencia suficiente
- una variante que conserve resultados aceptables `out-of-sample` merece mayor atención
- la robustez importa más que una optimización agresiva de parámetros

### Alcance Actual de Variantes

La comparativa principal de esta fase se centra en:

- estrategia base `swing_risk_managed`
- `Flexible Entry`
- `Calmer Exit`
- `Wider ATR Stop`

La variante `Percent Stop` permanece documentada y disponible para análisis adicional, pero no forma parte de la comparativa principal automatizada de esta fase.
