"""Tests de indicadores y helpers de cruce."""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategy import (
    atr,
    crossed_above_level,
    crossed_above_series,
    crossed_below_series,
    rsi_wilder,
    sma,
)


def test_sma_computes_expected_last_value() -> None:
    values = [1, 2, 3, 4, 5]
    result = sma(values, 3)
    assert result.iloc[-1] == 4


def test_rsi_wilder_stays_within_expected_bounds() -> None:
    values = pd.Series(np.linspace(100, 120, 50))
    result = rsi_wilder(values, 14)
    assert result.between(0, 100).all()


def test_rsi_wilder_returns_neutral_value_for_flat_series() -> None:
    values = pd.Series([100.0] * 20)
    result = rsi_wilder(values, 14)
    assert result.iloc[-1] == 50


def test_atr_returns_positive_values_after_warmup() -> None:
    close = pd.Series([10, 11, 12, 11, 13, 14, 13, 15], dtype=float)
    high = close + 1
    low = close - 1
    result = atr(high, low, close, period=3)
    assert result.iloc[-1] > 0


def test_crossed_above_level_detects_valid_cross() -> None:
    series = [50, 54, 56]
    assert crossed_above_level(series, 55) is True


def test_crossed_above_series_detects_cross() -> None:
    series_a = [1, 2, 4]
    series_b = [3, 3, 3]
    assert crossed_above_series(series_a, series_b) is True


def test_crossed_below_series_detects_cross() -> None:
    series_a = [4, 3, 1]
    series_b = [2, 2, 2]
    assert crossed_below_series(series_a, series_b) is True
