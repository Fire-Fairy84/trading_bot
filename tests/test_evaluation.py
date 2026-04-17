"""Tests de la capa de evaluación y partición temporal."""

from __future__ import annotations

import pandas as pd
import pytest

from evaluation import (
    SWING_VARIANT_NAMES,
    BacktestConfig,
    extract_metrics,
    run_all_tests,
    split_train_test,
    summarize_variant_takeaways,
)


def test_split_train_test_returns_expected_lengths(sample_ohlcv_df: pd.DataFrame) -> None:
    train_df, test_df = split_train_test(sample_ohlcv_df, split_ratio=0.7)
    assert len(train_df) == 224
    assert len(test_df) == 96


def test_split_train_test_rejects_invalid_ratio(sample_ohlcv_df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        split_train_test(sample_ohlcv_df, split_ratio=1.0)


def test_extract_metrics_maps_expected_fields() -> None:
    stats = pd.Series(
        {
            "Start": pd.Timestamp("2023-01-01"),
            "End": pd.Timestamp("2023-12-31"),
            "Return [%]": 10.126,
            "Buy & Hold Return [%]": 8.0,
            "Max. Drawdown [%]": -5.5,
            "Sharpe Ratio": 1.234,
            "# Trades": 4,
            "Win Rate [%]": 50.0,
            "Profit Factor": 1.5,
        }
    )
    metrics = extract_metrics(stats)

    assert metrics["return_pct"] == 10.13
    assert metrics["buy_hold_return_pct"] == 8.0
    assert metrics["vs_buy_hold_pct"] == 2.13
    assert metrics["trades"] == 4


def test_run_all_tests_returns_expected_shape(sample_ohlcv_df: pd.DataFrame) -> None:
    summary = run_all_tests({"SYNTH_1d": sample_ohlcv_df}, BacktestConfig())
    assert len(summary) == 14
    assert set(summary["sample"]) == {"in_sample", "out_of_sample"}
    assert set(summary["strategy"]) == {
        "swing_risk_managed",
        "swing_flexible_entry",
        "swing_calmer_exit",
        "swing_wider_atr_stop",
        "swing_percent_stop",
        "buy_and_hold",
        "sma_cross_benchmark",
    }


def test_run_all_tests_can_focus_on_swing_variants(sample_ohlcv_df: pd.DataFrame) -> None:
    summary = run_all_tests(
        {"SYNTH_1d": sample_ohlcv_df},
        BacktestConfig(),
        strategy_names=SWING_VARIANT_NAMES,
    )
    assert len(summary) == 8
    assert set(summary["strategy"]) == set(SWING_VARIANT_NAMES)


def test_summarize_variant_takeaways_mentions_best_strategy() -> None:
    summary = pd.DataFrame(
        [
            {
                "sample": "out_of_sample",
                "strategy": "swing_risk_managed",
                "return_pct": 10.0,
                "max_drawdown_pct": -8.0,
                "trades": 5,
            },
            {
                "sample": "out_of_sample",
                "strategy": "swing_flexible_entry",
                "return_pct": 12.0,
                "max_drawdown_pct": -8.5,
                "trades": 7,
            },
        ]
    )
    text = summarize_variant_takeaways(summary)
    assert "swing_flexible_entry" in text


def test_summarize_variant_takeaways_keeps_dataset_baselines_separate() -> None:
    summary = pd.DataFrame(
        [
            {
                "dataset": "AAA",
                "sample": "out_of_sample",
                "strategy": "swing_risk_managed",
                "return_pct": 1.0,
                "max_drawdown_pct": -5.0,
                "trades": 1,
            },
            {
                "dataset": "AAA",
                "sample": "out_of_sample",
                "strategy": "swing_flexible_entry",
                "return_pct": 2.0,
                "max_drawdown_pct": -5.0,
                "trades": 2,
            },
            {
                "dataset": "BBB",
                "sample": "out_of_sample",
                "strategy": "swing_risk_managed",
                "return_pct": 50.0,
                "max_drawdown_pct": -20.0,
                "trades": 5,
            },
            {
                "dataset": "BBB",
                "sample": "out_of_sample",
                "strategy": "swing_flexible_entry",
                "return_pct": 40.0,
                "max_drawdown_pct": -10.0,
                "trades": 6,
            },
        ]
    )

    text = summarize_variant_takeaways(summary)

    assert "swing_flexible_entry" in text
    assert "BBB" in text
    assert "cambia el retorno en -10.00 puntos" in text
