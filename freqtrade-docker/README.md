# Freqtrade con Docker

Subproyecto educativo para aprender a usar `Freqtrade` con `Docker` sin clonar el repositorio oficial y sin tocar el core.

## Qué incluye

- imagen oficial de `Freqtrade`
- carpeta `user_data/` montada desde tu máquina
- estrategia custom en `user_data/strategies/`
- configuración preparada para:
  - `download-data`
  - `backtesting`
  - `dry-run`

## Estructura

```text
freqtrade-docker/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── user_data/
    ├── config.json
    ├── data/
    ├── logs/
    └── strategies/
        └── MiEstrategia.py
```

## Antes de empezar

1. Instala `Docker Desktop` en Windows o macOS, o `Docker Engine + Docker Compose` en Linux.
2. Copia `.env.example` a `.env`.
3. Revisa `user_data/config.json`.

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

```bash
docker compose run --rm freqtrade download-data --config /freqtrade/user_data/config.json --strategy MiEstrategia --timeframe 1h --timerange 20240101-
```

## Ejecutar backtesting

```bash
docker compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.json --strategy MiEstrategia --timeframe 1h
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
