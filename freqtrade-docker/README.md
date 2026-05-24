# Freqtrade con Docker

Entorno de validación operativa para la parte `Freqtrade` del repositorio.

Mientras `src/` se usa como laboratorio de investigación con `backtesting.py`, esta carpeta se usa para ejecutar backtesting, descarga de datos y `dry-run` sobre `crypto spot` con `Freqtrade` y `Docker`, sin tocar el core del framework.

El objetivo aquí no es añadir más complejidad, sino mantener una configuración reproducible y separada del resto del código.

## Qué incluye

- imagen oficial de `Freqtrade`
- carpeta `user_data/` montada desde tu máquina
- estrategia custom en `user_data/strategies/`
- configuración preparada para `download-data`, `backtesting` y `dry-run`

## Estructura

```text
freqtrade-docker/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── user_data/
    ├── config.json
    ├── config.validation.json
    ├── data/
    ├── logs/
    └── strategies/
        └── my_strategy.py
```

## Antes de empezar

1. Instala `Docker Desktop` en Windows o macOS, o `Docker Engine + Docker Compose` en Linux.
2. Copia `.env.example` a `.env`.
3. Revisa `user_data/config.json` o `user_data/config.validation.json`, según el flujo que quieras usar.

## Crear `.env`

### Linux/macOS

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

## Descargar datos

### Config base

```bash
docker compose run --rm freqtrade download-data --config /freqtrade/user_data/config.json --timeframe 1h --timerange 20240101-
```

### Config de validación multi-par

```bash
docker compose run --rm freqtrade download-data --prepend --config /freqtrade/user_data/config.validation.json --timeframe 4h --timerange 20240101-20260331
```

## Ejecutar backtesting

Backtest rápido con la configuración base:

```bash
docker compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.json --strategy MiEstrategia --timeframe 1h
```

Backtest de validación con la variante swing:

```bash
docker compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.validation.json --strategy MiEstrategiaFaseB --timeframe 4h --timerange 20240401-20260331
```

## Ejecutar dry-run

```bash
docker compose up freqtrade
```

## Ver logs

```bash
docker compose logs -f freqtrade
```

## Parar el contenedor

```bash
docker compose down
```

## Nota

Esta carpeta no intenta sustituir la parte analítica de `src/`. Su función es mantener una base reproducible para validar estrategias dentro del flujo de `Freqtrade`.
