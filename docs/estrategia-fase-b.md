# Informe breve: cierre y estrategia a seguir tras la fase B

## Situación actual

La fase B ya deja una base útil:

- estrategia swing principal implementada
- indicadores y reglas separadas con claridad
- gestión de riesgo mínima integrada
- varias variantes comparables
- validación `in-sample` / `out-of-sample`
- tests unitarios para indicadores, sizing y evaluación

Esto significa que el proyecto ya está en un punto correcto para dejar de "añadir ideas" y empezar a exigir más evidencia.

## Decisión de cierre

La fase B queda cerrada con esta decisión:

- variante candidata para promoción a fase C: `swing_calmer_exit`
- alternativa secundaria: `swing_wider_atr_stop`
- variante descartada como candidata principal: `swing_flexible_entry`

La decisión no implica que `swing_calmer_exit` sea una estrategia robusta en sentido fuerte. Implica que, con la evidencia disponible en esta fase, es la versión más razonable para portar primero a un entorno más operativo.

## Evidencia actual

La promoción se apoya en los resultados `out-of-sample` actuales sobre `SPY 1d`:

- `swing_risk_managed`: `8.00%` de retorno, `-2.11%` de max drawdown, `8` trades
- `swing_calmer_exit`: `7.43%` de retorno, `-2.27%` de max drawdown, `9` trades
- `swing_wider_atr_stop`: `5.97%` de retorno, `-1.72%` de max drawdown, `8` trades
- `swing_flexible_entry`: `-2.06%` de retorno, `-4.66%` de max drawdown, `11` trades

La variante base obtiene el mayor retorno absoluto, pero `swing_calmer_exit` queda muy cerca y además valida mejor la hipótesis de trabajo más interesante de esta fase: reducir la agresividad de salida parece aportar más que flexibilizar la entrada.

La lectura cualitativa es:

- `Calmer Exit` mejora la portabilidad conceptual porque simplifica la idea táctica de salida
- `Wider ATR Stop` queda como alternativa defensiva si más adelante se quiere priorizar contención de drawdown
- `Flexible Entry` pierde fuerza como candidata al mostrar peor comportamiento fuera de muestra

## Prioridades inmediatas

- documentar explícitamente la decisión de promoción
- tratar `swing_calmer_exit` como versión base de la siguiente etapa
- conservar `swing_wider_atr_stop` como referencia secundaria
- evitar nuevas iteraciones menores en `backtesting.py` antes de completar la portabilidad

## Estrategia recomendada

La siguiente estrategia de trabajo debería ser ordenada y pragmática:

1. usar `swing_calmer_exit` como candidata principal en fase C
2. replicar la lógica en Freqtrade sin reoptimizar reglas durante la portabilidad
3. comparar el comportamiento del port con la implementación actual para detectar diferencias de framework
4. dejar la validación adicional de robustez para una iteración posterior, ya sobre una versión funcional en el nuevo entorno

## Riesgos a evitar

- confundir un buen `in-sample` con una ventaja real
- sobreajustar RSI, ATR o stops con demasiadas pruebas pequeñas
- añadir complejidad antes de demostrar robustez básica
- evaluar solo retorno sin mirar drawdown y estabilidad

## Recomendación final

La mejor decisión práctica en este punto es dejar cerrada la fase B y avanzar a fase C con una candidata explícita. La promoción de `swing_calmer_exit` debe entenderse como una decisión de continuidad con evidencia suficiente para seguir aprendiendo, no como una validación final de robustez.
