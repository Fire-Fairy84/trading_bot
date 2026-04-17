"""Helpers para evaluar estrategias sobre múltiples datasets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from backtesting import Backtest

from strategy import (
    BuyAndHoldStrategy,
    CalmerExitSwingStrategy,
    FlexibleEntrySwingStrategy,
    PercentStopSwingStrategy,
    RiskManagedSwingStrategy,
    SmaCrossBenchmarkStrategy,
    WiderAtrStopSwingStrategy,
)


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
    "swing_flexible_entry": FlexibleEntrySwingStrategy,
    "swing_calmer_exit": CalmerExitSwingStrategy,
    "swing_wider_atr_stop": WiderAtrStopSwingStrategy,
    "swing_percent_stop": PercentStopSwingStrategy,
    "buy_and_hold": BuyAndHoldStrategy,
    "sma_cross_benchmark": SmaCrossBenchmarkStrategy,
}

SWING_VARIANT_NAMES = [
    "swing_risk_managed",
    "swing_flexible_entry",
    "swing_calmer_exit",
    "swing_wider_atr_stop",
]


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
) -> tuple[Backtest, pd.Series, dict[str, Any]]:
    """Ejecuta una estrategia concreta sobre un DataFrame OHLCV."""
    strategy_class = STRATEGY_MAP[strategy_name]
    backtest = build_backtest(dataframe, strategy_class, config)
    stats = backtest.run()
    metrics = extract_metrics(stats)
    return backtest, stats, metrics


def run_strategy_suite(
    dataframe: pd.DataFrame,
    config: BacktestConfig,
    strategy_names: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Ejecuta un conjunto concreto de estrategias sobre un dataset."""
    results: list[dict[str, Any]] = []
    strategy_names = strategy_names or list(STRATEGY_MAP)
    for strategy_name in strategy_names:
        _, _, metrics = run_strategy(dataframe, strategy_name, config)
        results.append({"strategy": strategy_name, **metrics})
    return results


def run_all_tests(
    data_dict: dict[str, pd.DataFrame],
    config: BacktestConfig | None = None,
    strategy_names: list[str] | None = None,
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
            for result in run_strategy_suite(sample_df, config, strategy_names):
                rows.append(
                    {
                        "dataset": dataset_name,
                        "sample": sample_name,
                        **result,
                    }
                )

    return pd.DataFrame(rows)


def summarize_variant_takeaways(summary: pd.DataFrame) -> str:
    """Genera una lectura breve de la comparativa out-of-sample.

    Regla simple:
    - priorizamos retorno
    - penalizamos estrategias que empeoran demasiado el drawdown
    - usamos el resultado out-of-sample, que es el más útil para decidir
    """
    out_of_sample = summary.loc[summary["sample"] == "out_of_sample"].copy()
    if out_of_sample.empty:
        return "No hay resultados out-of-sample para interpretar."

    if "dataset" in out_of_sample.columns:
        dataset_groups = out_of_sample.groupby("dataset", sort=False)
    else:
        dataset_groups = [(None, out_of_sample)]

    best_candidate: tuple[float, pd.Series, pd.Series] | None = None

    for dataset_name, dataset_rows in dataset_groups:
        original_row = dataset_rows.loc[
            dataset_rows["strategy"] == "swing_risk_managed"
        ]
        if original_row.empty:
            continue

        original = original_row.iloc[0]

        for _, row in dataset_rows.iterrows():
            if row["strategy"] == "swing_risk_managed":
                continue

            drawdown_penalty = max(
                0.0,
                abs(row["max_drawdown_pct"]) - abs(original["max_drawdown_pct"]),
            )
            score = float(row["return_pct"]) - drawdown_penalty

            if best_candidate is None or score > best_candidate[0]:
                best_candidate = (score, row, original)

    if best_candidate is None:
        return "Faltan variantes comparables junto a la estrategia original."

    _, best_row, original = best_candidate

    trade_delta = int(best_row["trades"] - original["trades"])
    return_delta = round(float(best_row["return_pct"] - original["return_pct"]), 2)
    drawdown_delta = round(
        abs(float(best_row["max_drawdown_pct"])) - abs(float(original["max_drawdown_pct"])),
        2,
    )
    dataset_prefix = ""
    if "dataset" in best_row.index:
        dataset_prefix = f"en {best_row['dataset']} "

    return (
        f"La versión más prometedora parece ser '{best_row['strategy']}' {dataset_prefix}en out-of-sample: "
        f"retorno {best_row['return_pct']:.2f}%, "
        f"drawdown máximo {best_row['max_drawdown_pct']:.2f}% "
        f"y {best_row['trades']} trades. "
        f"Frente a la original, cambia el retorno en {return_delta:+.2f} puntos, "
        f"el drawdown en {drawdown_delta:+.2f} puntos y el número de trades en {trade_delta:+d}. "
        "La lectura práctica es simple: si gana más sin empeorar demasiado la caída, "
        "merece ser la siguiente candidata para validar fuera de muestra."
    )
