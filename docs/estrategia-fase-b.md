# Informe breve: estrategia a seguir tras la fase B

## Situación actual

La fase B ya deja una base útil:

- estrategia swing principal implementada
- indicadores y reglas separadas con claridad
- gestión de riesgo mínima integrada
- varias variantes comparables
- validación `in-sample` / `out-of-sample`
- tests unitarios para indicadores, sizing y evaluación

Esto significa que el proyecto ya está en un punto correcto para dejar de "añadir ideas" y empezar a exigir más evidencia.

## Estrategia recomendada

La siguiente estrategia de trabajo debería ser conservadora y ordenada:

1. consolidar una variante candidata en vez de seguir creando muchas más
2. validar esa candidata en más datasets, activos o marcos temporales
3. revisar si el comportamiento aguanta costes, drawdown y número de operaciones razonables
4. documentar qué mejora aporta cada cambio y cuáles no merecen seguir
5. solo después mover la estrategia a una fase más operativa como Freqtrade

## Prioridades inmediatas

- comparar la variante base contra las variantes swing en más muestras
- evitar optimización excesiva de parámetros sobre un único activo
- registrar conclusiones simples por experimento: qué cambió, qué mejoró, qué empeoró
- elegir una sola versión para promoción a fase C

## Riesgos a evitar

- confundir un buen `in-sample` con una ventaja real
- sobreajustar RSI, ATR o stops con demasiadas pruebas pequeñas
- añadir complejidad antes de demostrar robustez básica
- evaluar solo retorno sin mirar drawdown y estabilidad

## Recomendación final

La mejor dirección ahora no es "hacer la estrategia más compleja", sino "hacer la validación más seria". Si una variante mantiene resultados aceptables fuera de muestra y no degrada demasiado el drawdown, esa debería ser la candidata para la siguiente fase.
