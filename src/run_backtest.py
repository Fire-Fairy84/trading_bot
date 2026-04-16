"""Runner principal para descargar datos y evaluar estrategias."""

from __future__ import annotations

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
DEFAULT_START = "2015-01-01"
DEFAULT_END = "2025-01-01"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def build_demo_data_dict(dataframe: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Devuelve una estructura lista para usar con run_all_tests()."""
    return {"SPY_1d": dataframe}


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
    html_paths: list[Path] = []
    train_df, test_df = split_train_test(dataframe, config.split_ratio)

    for sample_name, sample_df in [("in_sample", train_df), ("out_of_sample", test_df)]:
        for strategy_name in SWING_VARIANT_NAMES:
            backtest, _, _ = run_strategy(sample_df, strategy_name, config)
            html_path = REPORTS_DIR / f"{dataset_name}_{sample_name}_{strategy_name}.html"
            backtest.plot(filename=str(html_path), open_browser=False)
            html_paths.append(html_path)

    return html_paths


def load_demo_dataset() -> pd.DataFrame:
    """Usa primero el CSV local para no depender de descarga en cada ejecución."""
    local_csv_path = Path(__file__).resolve().parent.parent / "data" / f"{DEFAULT_SYMBOL}_1d.csv"
    csv_path = local_csv_path

    if not local_csv_path.exists():
        csv_path = download_ohlcv(
            symbol=DEFAULT_SYMBOL,
            start=DEFAULT_START,
            end=DEFAULT_END,
            interval="1d",
        )

    return load_ohlcv(csv_path)


def print_compact_console_summary(
    dataset_name: str,
    dataframe: pd.DataFrame,
    summary: pd.DataFrame,
    csv_path: Path,
    md_path: Path,
    html_paths: list[Path],
) -> None:
    """Deja en consola solo un resumen corto y dónde mirar el detalle."""
    print(f"Dataset: {dataset_name}")
    print(f"Filas: {len(dataframe)}")
    print(f"Rango: {dataframe.index.min().date()} -> {dataframe.index.max().date()}")
    print(f"CSV datos: {Path('data') / f'{DEFAULT_SYMBOL}_1d.csv'}")
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
    """Ejemplo completo de uso sobre un dataset diario de SPY."""
    warnings.filterwarnings(
        "ignore",
        category=FutureWarning,
        module=r"backtesting\..*",
    )

    dataframe = load_demo_dataset()

    config = BacktestConfig(
        initial_cash=10_000,
        commission=0.001,
        spread=0.0005,
        split_ratio=0.7,
    )

    data_dict = build_demo_data_dict(dataframe)
    summary = run_all_tests(data_dict, config, strategy_names=SWING_VARIANT_NAMES)
    csv_report_path, markdown_report_path = save_reports(summary, "SPY_1d")
    html_report_paths = save_html_reports("SPY_1d", dataframe, config)
    print_compact_console_summary(
        "SPY_1d",
        dataframe,
        summary,
        csv_report_path,
        markdown_report_path,
        html_report_paths,
    )


if __name__ == "__main__":
    main()
