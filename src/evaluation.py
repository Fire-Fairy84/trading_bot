"""Helpers para evaluar estrategias sobre múltiples datasets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from backtesting import Backtest

from strategy import BuyAndHoldStrategy, RiskManagedSwingStrategy, SmaCrossBenchmarkStrategy


@dataclass(frozen=True)
class BacktestConfig:
    initial_cash: float = 10_000
    commission: float = 0.001
    spread: float = 0.0005
    trade_on_close: bool = False
    exclusive_orders: bool = True
    finalize_trades: bool = True
    split_ratio: float = 0.7


STRATEGY_MAP = {
    "swing_risk_managed": RiskManagedSwingStrategy,
    "buy_and_hold": BuyAndHoldStrategy,
    "sma_cross_benchmark": SmaCrossBenchmarkStrategy,
}


def build_backtest(
    dataframe: pd.DataFrame,
    strategy_class,
    config: BacktestConfig,
) -> Backtest:
    """Construye un Backtest con costes consistentes para todas las estrategias."""
    return Backtest(
        dataframe,
        strategy_class,
        cash=config.initial_cash,
        commission=config.commission,
        spread=config.spread,
        exclusive_orders=config.exclusive_orders,
        trade_on_close=config.trade_on_close,
        finalize_trades=config.finalize_trades,
    )


def split_train_test(
    dataframe: pd.DataFrame, split_ratio: float
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa un DataFrame temporalmente en in-sample y out-of-sample."""
    if not 0 < split_ratio < 1:
        raise ValueError("split_ratio debe estar entre 0 y 1.")

    split_index = int(len(dataframe) * split_ratio)
    train_df = dataframe.iloc[:split_index].copy()
    test_df = dataframe.iloc[split_index:].copy()

    if train_df.empty or test_df.empty:
        raise ValueError("La partición temporal dejó un bloque vacío.")

    return train_df, test_df


def extract_metrics(stats: pd.Series) -> dict[str, Any]:
    """Extrae métricas comparables de la salida de backtesting.py."""
    return {
        "start": stats["Start"],
        "end": stats["End"],
        "return_pct": round(float(stats["Return [%]"]), 2),
        "buy_hold_return_pct": round(float(stats["Buy & Hold Return [%]"]), 2),
        "vs_buy_hold_pct": round(
            float(stats["Return [%]"] - stats["Buy & Hold Return [%]"]), 2
        ),
        "max_drawdown_pct": round(float(stats["Max. Drawdown [%]"]), 2),
        "sharpe_ratio": round(float(stats.get("Sharpe Ratio", float("nan"))), 2),
        "trades": int(stats.get("# Trades", 0)),
        "win_rate_pct": round(float(stats.get("Win Rate [%]", float("nan"))), 2),
        "profit_factor": round(float(stats.get("Profit Factor", float("nan"))), 2),
    }


def print_metrics(label: str, metrics: dict[str, Any]) -> None:
    """Imprime un resumen legible para consola."""
    print(f"\n=== {label} ===")
    print(f"Start: {metrics['start']}")
    print(f"End: {metrics['end']}")
    print(f"Return [%]: {metrics['return_pct']:.2f}")
    print(f"Buy & Hold Return [%]: {metrics['buy_hold_return_pct']:.2f}")
    print(f"Strategy vs Buy & Hold [%]: {metrics['vs_buy_hold_pct']:.2f}")
    print(f"Max. Drawdown [%]: {metrics['max_drawdown_pct']:.2f}")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"# Trades: {metrics['trades']}")
    print(f"Win Rate [%]: {metrics['win_rate_pct']:.2f}")
    print(f"Profit Factor: {metrics['profit_factor']:.2f}")


def run_strategy(
    dataframe: pd.DataFrame,
    strategy_name: str,
    config: BacktestConfig,
) -> tuple[pd.Series, dict[str, Any]]:
    """Ejecuta una estrategia concreta sobre un DataFrame OHLCV."""
    strategy_class = STRATEGY_MAP[strategy_name]
    backtest = build_backtest(dataframe, strategy_class, config)
    stats = backtest.run()
    metrics = extract_metrics(stats)
    return stats, metrics


def run_strategy_suite(
    dataframe: pd.DataFrame,
    config: BacktestConfig,
) -> list[dict[str, Any]]:
    """Ejecuta las tres estrategias sobre un único dataset."""
    results: list[dict[str, Any]] = []
    for strategy_name in STRATEGY_MAP:
        _, metrics = run_strategy(dataframe, strategy_name, config)
        results.append({"strategy": strategy_name, **metrics})
    return results


def run_all_tests(
    data_dict: dict[str, pd.DataFrame],
    config: BacktestConfig | None = None,
) -> pd.DataFrame:
    """Corre in-sample y out-of-sample sobre múltiples activos o timeframes.

    Las keys de data_dict pueden ser cosas como:
    - SPY_1d
    - QQQ_1d
    - BTC-USD_4h
    """
    config = config or BacktestConfig()
    rows: list[dict[str, Any]] = []

    for dataset_name, dataframe in data_dict.items():
        train_df, test_df = split_train_test(dataframe, config.split_ratio)

        for sample_name, sample_df in [("in_sample", train_df), ("out_of_sample", test_df)]:
            for result in run_strategy_suite(sample_df, config):
                rows.append(
                    {
                        "dataset": dataset_name,
                        "sample": sample_name,
                        **result,
                    }
                )

    return pd.DataFrame(rows)
