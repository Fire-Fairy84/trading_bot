"""Configuración común para pytest."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture
def sample_ohlcv_df() -> pd.DataFrame:
    """Crea un OHLCV sintético con longitud suficiente para SMA 200."""
    periods = 320
    index = pd.date_range("2022-01-01", periods=periods, freq="D")

    trend = np.linspace(100, 160, periods)
    oscillation = 3 * np.sin(np.linspace(0, 12 * np.pi, periods))
    close = trend + oscillation
    open_ = close - 0.4
    high = close + 1.0
    low = close - 1.0
    volume = np.full(periods, 1_000_000, dtype=int)

    return pd.DataFrame(
        {
            "Open": open_,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": volume,
        },
        index=index,
    )
