"""Runner principal para descargar datos y evaluar estrategias."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import warnings

import pandas as pd

from evaluation import (
    SWING_VARIANT_NAMES,
    BacktestConfig,
    run_all_tests,
    run_strategy,
    split_train_test,
    summarize_variant_takeaways,
)
from load_data import download_ohlcv, load_ohlcv


DEFAULT_SYMBOL = "SPY"
DEFAULT_INTERVAL = "1d"
DEFAULT_START = "2015-01-01"
DEFAULT_END = "2025-01-01"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


@dataclass(frozen=True)
class RunSettings:
    symbol: str = DEFAULT_SYMBOL
    interval: str = DEFAULT_INTERVAL
    start: str = DEFAULT_START
    end: str = DEFAULT_END
    dataset_name: str | None = None

    @property
    def resolved_dataset_name(self) -> str:
        return self.dataset_name or f"{self.symbol}_{self.interval}"

    @property
    def local_csv_path(self) -> Path:
        return Path(__file__).resolve().parent.parent / "data" / f"{self.symbol}_{self.interval}.csv"


def parse_args() -> RunSettings:
    """Parsea argumentos opcionales para no dejar el runner clavado a SPY."""
    parser = argparse.ArgumentParser(description="Run backtests for a local or downloaded OHLCV dataset.")
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--interval", default=DEFAULT_INTERVAL)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    parser.add_argument("--dataset-name")
    args = parser.parse_args()
    return RunSettings(
        symbol=args.symbol,
        interval=args.interval,
        start=args.start,
        end=args.end,
        dataset_name=args.dataset_name,
    )


def build_data_dict(dataset_name: str, dataframe: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Devuelve una estructura lista para usar con run_all_tests()."""
    return {dataset_name: dataframe}


def save_reports(summary: pd.DataFrame, dataset_name: str) -> tuple[Path, Path]:
    """Guarda los resultados en CSV y Markdown para revisión cómoda."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORTS_DIR / f"{dataset_name}_summary.csv"
    md_path = REPORTS_DIR / f"{dataset_name}_summary.md"

    summary.to_csv(csv_path, index=False)

    markdown_lines = [
        f"# Backtest Summary: {dataset_name}",
        "",
        "```text",
        summary.to_string(index=False),
        "```",
        "",
    ]
    md_path.write_text("\n".join(markdown_lines), encoding="utf-8")
    return csv_path, md_path


def save_html_reports(
    dataset_name: str,
    dataframe: pd.DataFrame,
    config: BacktestConfig,
) -> list[Path]:
    """Genera un HTML por estrategia y por muestra temporal."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    html_paths: list[Path] = []
    train_df, test_df = split_train_test(dataframe, config.split_ratio)

    for sample_name, sample_df in [("in_sample", train_df), ("out_of_sample", test_df)]:
        for strategy_name in SWING_VARIANT_NAMES:
            backtest, _, _ = run_strategy(sample_df, strategy_name, config)
            html_path = REPORTS_DIR / f"{dataset_name}_{sample_name}_{strategy_name}.html"
            backtest.plot(filename=str(html_path), open_browser=False)
            html_paths.append(html_path)

    return html_paths


def load_dataset(settings: RunSettings) -> tuple[pd.DataFrame, Path]:
    """Usa primero el CSV local y descarga solo si el dataset no existe."""
    csv_path = settings.local_csv_path

    if not csv_path.exists():
        csv_path = download_ohlcv(
            symbol=settings.symbol,
            start=settings.start,
            end=settings.end,
            interval=settings.interval,
        )

    return load_ohlcv(csv_path), csv_path


def print_compact_console_summary(
    dataset_name: str,
    dataframe: pd.DataFrame,
    data_csv_path: Path,
    summary: pd.DataFrame,
    csv_path: Path,
    md_path: Path,
    html_paths: list[Path],
) -> None:
    """Deja en consola solo un resumen corto y dónde mirar el detalle."""
    print(f"Dataset: {dataset_name}")
    print(f"Filas: {len(dataframe)}")
    print(f"Rango: {dataframe.index.min().date()} -> {dataframe.index.max().date()}")
    print(f"CSV datos: {data_csv_path}")
    print(f"Resumen CSV: {csv_path}")
    print(f"Resumen Markdown: {md_path}")
    print("Reportes HTML:")
    for html_path in html_paths:
        print(f"- {html_path}")
    print("\nVista rápida:")
    columns = [
        "dataset",
        "sample",
        "strategy",
        "return_pct",
        "buy_hold_return_pct",
        "max_drawdown_pct",
        "trades",
        "win_rate_pct",
        "profit_factor",
    ]
    print(summary[columns].to_string(index=False))
    print("\nLectura breve:")
    print(summarize_variant_takeaways(summary))


def main() -> None:
    """Ejecuta el flujo completo de backtesting sobre un dataset configurable."""
    warnings.filterwarnings(
        "ignore",
        category=FutureWarning,
        module=r"backtesting\..*",
    )

    settings = parse_args()
    dataset_name = settings.resolved_dataset_name

    dataframe, data_csv_path = load_dataset(settings)

    config = BacktestConfig(
        initial_cash=10_000,
        commission=0.001,
        spread=0.0005,
        split_ratio=0.7,
    )

    data_dict = build_data_dict(dataset_name, dataframe)
    summary = run_all_tests(data_dict, config, strategy_names=SWING_VARIANT_NAMES)
    csv_report_path, markdown_report_path = save_reports(summary, dataset_name)
    html_report_paths = save_html_reports(dataset_name, dataframe, config)
    print_compact_console_summary(
        dataset_name,
        dataframe,
        data_csv_path,
        summary,
        csv_report_path,
        markdown_report_path,
        html_report_paths,
    )


if __name__ == "__main__":
    main()
