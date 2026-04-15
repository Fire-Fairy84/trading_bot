"""Funciones para descargar, guardar y cargar datos OHLCV."""

from pathlib import Path

import pandas as pd
import yfinance as yf


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def download_ohlcv(
    symbol: str = "SPY",
    start: str = "2015-01-01",
    end: str = "2025-01-01",
    interval: str = "1d",
    force: bool = False,
) -> Path:
    """Descarga datos OHLCV desde Yahoo Finance y los guarda en CSV.

    OHLCV significa Open, High, Low, Close, Volume.
    Es el formato mínimo típico para backtesting con velas.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = DATA_DIR / f"{symbol}_{interval}.csv"

    if csv_path.exists() and not force:
        return csv_path

    data = yf.download(
        tickers=symbol,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )

    if data.empty:
        raise ValueError(
            "No se descargaron datos. Revisa el ticker, la conexión o el rango de fechas."
        )

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.rename_axis("Date").reset_index()
    data = data[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    data.to_csv(csv_path, index=False)
    return csv_path


def load_ohlcv(csv_path: str | Path) -> pd.DataFrame:
    """Carga un CSV y lo deja listo para backtesting.py."""
    dataframe = pd.read_csv(csv_path, parse_dates=["Date"])
    dataframe = dataframe.sort_values("Date").set_index("Date")

    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    missing = [column for column in required_columns if column not in dataframe.columns]
    if missing:
        raise ValueError(f"Faltan columnas obligatorias en el CSV: {missing}")

    return dataframe[required_columns].dropna().copy()


def split_in_sample_out_of_sample(
    dataframe: pd.DataFrame, split_ratio: float = 0.7
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa los datos en dos bloques temporales.

    in-sample: tramo usado para desarrollar la idea.
    out-of-sample: tramo reservado para comprobar si la idea aguanta fuera
    de la muestra usada para diseñarla.
    """
    if not 0 < split_ratio < 1:
        raise ValueError("split_ratio debe estar entre 0 y 1.")

    split_index = int(len(dataframe) * split_ratio)
    in_sample = dataframe.iloc[:split_index].copy()
    out_of_sample = dataframe.iloc[split_index:].copy()

    if in_sample.empty or out_of_sample.empty:
        raise ValueError("La partición dejó un bloque vacío. Usa más datos.")

    return in_sample, out_of_sample
