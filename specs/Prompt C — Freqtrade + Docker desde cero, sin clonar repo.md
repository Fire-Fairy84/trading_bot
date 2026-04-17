
Quiero que actúes como mi mentor técnico y profesor paso a paso para enseñarme a montar Freqtrade con Docker desde cero, sin clonar ni forkear el repositorio de Freqtrade, explicándolo todo en español para una persona junior.

CONTEXTO
- Soy junior.
- Sé algo de Python, Java y SQL.
- Tengo poca experiencia con Docker.
- Quiero aprender bien cómo funciona Freqtrade.
- No quiero tocar el core de Freqtrade si no es necesario.
- Quiero que me expliques muy bien por qué no hace falta clonar el repo completo para usar estrategias custom.
- Quiero preparar un entorno limpio para:
  - backtesting
  - download-data
  - dry-run
- NO quiero live trading todavía.
- Quiero todo en español, pero manteniendo los términos técnicos en INGLÉS y explicándolos.

OBJETIVO DE ESTE PROMPT
Quiero que me ayudes a montar desde cero un proyecto Freqtrade funcional con Docker, usando la imagen oficial, una carpeta user_data y una estrategia custom, sin clonar el repo de Freqtrade.

FORMA DE TRABAJAR
- Ve paso a paso.
- No asumas que sé Docker.
- Antes de crear archivos, explica para qué sirve cada uno.
- Explica cada comando.
- Explica cada concepto:
  - image
  - container
  - volume
  - bind mount
  - env_file
  - command
  - port
  - restart policy
- Si algo puede romperse, adviértelo.
- Si hay varias formas de hacerlo, elige la más simple y robusta para un junior.
- Quiero una explicación larga, didáctica y concreta.
- Quiero que el resultado sea usable y entendible.

QUIERO QUE HAGAS SOLO ESTA FASE
FASE 3: MONTAJE DE FREQTRADE CON DOCKER

Necesito que hagas esto, en este orden:

1. Explícame qué es Freqtrade en español y para qué sirve.
2. Explícame por qué no necesito clonar ni forkear el repo de Freqtrade para usarlo.
3. Explícame la arquitectura correcta:
   - usar imagen oficial
   - montar user_data
   - guardar config y strategies fuera del core
4. Propón una estructura limpia de proyecto, por ejemplo:
   proyecto-freqtrade/
   ├── docker-compose.yml
   ├── .env.example
   ├── .gitignore
   ├── README.md
   └── user_data/
       ├── config.json
       ├── strategies/
       │   └── MiEstrategia.py
       ├── data/
       └── logs/
5. Enséñame los comandos para crear esa estructura:
   - Windows
   - Linux/macOS
6. Crea el contenido completo de:
   - docker-compose.yml
   - .env.example
   - .gitignore
   - README.md
   - user_data/config.json
   - user_data/strategies/MiEstrategia.py
7. Quiero que la estrategia sea simple y educativa, no compleja.
8. Explica cada archivo línea por línea.
9. Explícame por qué conviene o no conviene usar:
   - image: freqtradeorg/freqtrade:stable
   - o una versión fijada
10. Enséñame cómo levantar el contenedor con Docker Compose.
11. Enséñame cómo ver logs.
12. Enséñame cómo ejecutar:
   - download-data
   - backtesting
   - dry-run
13. Explica qué hace cada comando.
14. Explica qué resultados debería ver.
15. Dime errores comunes:
   - rutas mal montadas
   - config.json mal formado
   - estrategia no encontrada
   - permisos
   - problemas de volumen
16. Dime cómo solucionarlos.
17. Explícame claramente por qué todavía NO deberíamos pasar a live trading.
18. Al final, dame una checklist final de verificación.

IMPORTANTE
- Todo en español.
- Términos técnicos en inglés y explicados.
- No clonar repo de Freqtrade salvo que sea estrictamente imprescindible.
- No tocar el core.
- No live trading.
- No leverage.
- No complicar la estrategia.
- Quiero una respuesta muy detallada y pedagógica.

FORMATO DE SALIDA
Quiero que respondas con esta estructura:
1. Introducción y visión general
2. Conceptos clave de Docker y Freqtrade
3. Arquitectura recomendada
4. Estructura de carpetas
5. Creación de archivos
6. Código completo
7. Explicación línea por línea
8. Comandos de uso
9. Errores comunes y soluciones
10. Checklist final
11. Siguiente fase propuesta