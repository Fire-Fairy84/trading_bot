# Experiment Plan

## Goal

El objetivo de esta fase es determinar si pequeñas modificaciones sobre una estrategia swing base alteran de forma útil su equilibrio entre retorno, drawdown, frecuencia operativa y consistencia fuera de muestra.

La meta no es optimizar todos los parámetros, sino identificar qué tipos de cambios parecen prometedores y cuáles añaden complejidad sin evidencia suficiente.

## Base Strategy

La estrategia base es una estrategia swing long-only sobre `SPY` diario con las siguientes piezas:

- filtro de tendencia con `SMA 50 > SMA 200`
- confirmación de entrada mediante recuperación de momentum con `RSI`
- `stop loss` configurable
- `position sizing` basado en riesgo máximo del `1%` del equity por operación
- una sola posición activa a la vez

Esta versión base actúa como referencia principal para valorar si una variante representa una mejora real o solo un cambio superficial.

## Variants to Test

### Flexible Entry

Qué cambia:

- reduce la exigencia del umbral de entrada del `RSI`

Qué intenta probar:

- si una entrada algo menos estricta permite capturar más movimientos válidos
- si ese aumento de sensibilidad mejora el retorno sin degradar de forma evidente la calidad de las señales

### Calmer Exit

Qué cambia:

- elimina la salida por `RSI` en la lógica principal de salida
- activa un `trailing stop`

Qué intenta probar:

- si dejar respirar más las posiciones permite capturar tendencias más largas
- si un `trailing stop` protege beneficios mejor que una salida táctica excesivamente agresiva

### Wider ATR Stop

Qué cambia:

- aumenta la distancia del `ATR stop`

Qué intenta probar:

- si un stop más amplio reduce salidas por ruido normal de mercado
- si esa tolerancia adicional mejora la estabilidad sin deteriorar de forma excesiva el drawdown

### Percent Stop

Qué cambia:

- sustituye el `ATR stop` por un `stop` porcentual fijo

Qué intenta probar:

- si una lógica más simple y menos dependiente de volatilidad produce resultados aceptables
- si el coste de perder adaptación al contexto de mercado compensa o no la simplicidad

Nota de alcance actual:

- esta variante está implementada y documentada
- no forma parte de la comparativa principal automatizada de la fase B
- su evaluación debe considerarse complementaria o exploratoria

## Hypotheses

1. La variante `Flexible Entry` debería aumentar el número de operaciones y posiblemente el retorno bruto, pero puede reducir la calidad media de las entradas.
2. La variante `Calmer Exit` podría capturar tramos alcistas más largos y mejorar el retorno por trade, a costa de aceptar retrocesos intermedios mayores.
3. La variante `Wider ATR Stop` podría reducir salidas prematuras y mejorar la robustez, aunque también puede aumentar pérdidas por operación si la hipótesis falla.
4. La variante `Percent Stop` debería ser más simple de interpretar, pero probablemente será menos adaptable a distintos regímenes de volatilidad.

Estas hipótesis deben juzgarse por resultados agregados y no por ejemplos aislados de trades concretos.

## Evaluation Method

### Uso de In-Sample / Out-of-Sample

La evaluación se divide en dos bloques temporales:

- `in-sample`: tramo usado para desarrollo, comprensión y comparación inicial
- `out-of-sample`: tramo reservado para observar si la lógica conserva comportamiento razonable fuera del periodo usado para diseñarla

La separación temporal reduce el riesgo de sobreinterpretar mejoras derivadas de un ajuste implícito a una muestra concreta.

### Comparación de Resultados

Cada variante debe compararse con:

- la estrategia base
- los benchmarks (`Buy & Hold` y `SMA crossover`)
- sus propios resultados `in-sample` frente a `out-of-sample`

La comparación no debe hacerse solo por retorno final. Debe incorporar:

- cambio en `Max Drawdown`
- número de operaciones
- estabilidad relativa
- relación entre mejora de retorno y coste en riesgo adicional

En la implementación actual, la comparación cuantificada derivada está más formalizada frente a `Buy & Hold` que frente a `SMA crossover`. Por tanto, la lectura frente a `SMA crossover` debe hacerse hoy como contraste contextual y no como criterio automático resumido en una métrica específica.

## Success Criteria

Una variante puede considerarse candidata a mejora real si cumple la mayoría de las condiciones siguientes:

- mejora o mantiene el retorno `out-of-sample` frente a la estrategia base
- no empeora el `Max Drawdown` en una magnitud que invalide la mejora de retorno
- no depende de un número extremadamente pequeño de operaciones atípicas
- mantiene una lógica coherente y explicable
- no queda claramente por detrás de los benchmarks en la lectura global
- no introduce complejidad adicional desproporcionada respecto al beneficio observado

La mejora real debe entenderse como una mejora robusta, no como el mejor dato aislado de una tabla.

Como guía práctica para esta fase:

- una variante merece revisión adicional si mejora el retorno `out-of-sample` y no aumenta de forma evidente el drawdown
- una variante pierde prioridad si solo mejora `in-sample` o si su mejora depende de muy pocos trades
- si dos variantes ofrecen resultados parecidos, debe preferirse la más simple de explicar y mantener

## Notes

- Existe riesgo de `overfitting` incluso sin realizar una optimización formal. Cada ajuste manual de umbrales también puede sobreadaptar la estrategia.
- El hecho de trabajar con un solo activo y un solo timeframe limita la generalización de conclusiones.
- Un buen resultado `in-sample` no implica ventaja estructural.
- Un número alto de métricas puede dar falsa sensación de rigor si no se prioriza la consistencia `out-of-sample`.
- Los benchmarks simples son importantes porque obligan a justificar que la complejidad adicional aporta valor.
- La siguiente fase debería priorizar robustez experimental antes de ampliar mucho el número de reglas.
