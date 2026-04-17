

Quiero que actúes como mi mentor técnico y profesor paso a paso para enseñarme a validar una estrategia swing sencilla con backtesting.py, explicándolo todo en español para una persona junior.

CONTEXTO
- Ya tengo un proyecto base preparado.
- Quiero aprender a usar backtesting.py de forma correcta.
- No quiero humo ni promesas de rentabilidad.
- Quiero entender la lógica, las métricas y los límites del backtesting.
- Los términos técnicos deben ir en INGLÉS, pero explicados en español.
- Mi prioridad es aprender, no optimizar demasiado rápido.

OBJETIVO DE ESTE PROMPT
Quiero que me ayudes a:
1. montar una estrategia swing simple,
2. cargar datos históricos,
3. ejecutar un backtest,
4. interpretar resultados,
5. entender qué significa realmente validar una idea.

FORMA DE TRABAJAR
- Ve paso a paso.
- No asumas experiencia previa.
- Explica todo en español.
- Usa nombres técnicos en inglés y luego explícalos.
- Quiero que el código esté comentado.
- Después del código, quiero explicación línea por línea.
- Quiero entender también los errores típicos.
- No me lleves todavía a algo muy complejo.
- Prioriza claridad y criterio antes que sofisticación.

QUIERO QUE HAGAS SOLO ESTA FASE
FASE 2: PRIMER BACKTEST SERIO CON BACKTESTING.PY

Necesito que hagas esto, en este orden:

1. Explícame qué es backtesting.py en español y para qué sirve.
2. Explícame qué es una estrategia swing de forma simple.
3. Propón una estrategia swing sencilla y razonable para aprender.
   Ejemplo: cruce de medias + filtro RSI, o algo parecido.
   Pero quiero que elijas una opción simple, robusta y pedagógica.
4. Explícame por qué esa estrategia NO implica edge real automáticamente.
5. Crea los archivos necesarios, por ejemplo:
   - src/load_data.py
   - src/strategy.py
   - src/run_backtest.py
6. Si hace falta descargar datos, enséñame la opción más simple.
   Si usas yfinance u otra librería, explícalo.
7. Crea el código completo con comentarios.
8. Explica cada archivo línea por línea.
9. Enséñame a ejecutar el backtest desde terminal.
10. Explícame qué resultado debería aparecer.
11. Explícame las métricas básicas:
   - return
   - annual return
   - Sharpe ratio
   - max drawdown
   - win rate
   - profit factor
   - number of trades
12. Explícame cómo pensar críticamente sobre esas métricas.
13. Incluye fees y una aproximación simple de slippage si backtesting.py lo permite de forma razonable.
14. Explícame qué es overfitting y por qué es un riesgo.
15. Enséñame una forma básica de separar:
   - in-sample
   - out-of-sample
16. Dime qué señales indicarían que una estrategia NO merece seguir.
17. Dime qué señales indicarían que una estrategia quizá sí merece una segunda revisión.
18. Al final, dame una checklist de validación para esta fase.

IMPORTANTE
- No quiero optimización masiva todavía.
- No quiero hyperparameter search complejo todavía.
- No quiero Freqtrade todavía.
- No quiero live trading.
- Quiero una solución simple, limpia y muy explicada.
- Quiero que me enseñes también a desconfiar de un backtest bonito.

FORMATO DE SALIDA
Quiero que respondas con esta estructura:
1. Introducción y teoría mínima
2. Estrategia elegida y por qué
3. Estructura de archivos
4. Código completo
5. Explicación línea por línea
6. Cómo ejecutar
7. Cómo interpretar resultados
8. Riesgos y errores comunes
9. Qué sería una validación razonable
10. Checklist final
11. Siguiente fase propuesta