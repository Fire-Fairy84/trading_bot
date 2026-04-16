"""Runner principal para descargar datos y evaluar estrategias."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from evaluation import BacktestConfig, print_metrics, run_all_tests, run_strategy_suite
from load_data import download_ohlcv, load_ohlcv, split_in_sample_out_of_sample


DEFAULT_SYMBOL = "SPY"
DEFAULT_START = "2015-01-01"
DEFAULT_END = "2025-01-01"


def print_dataset_overview(name: str, dataframe: pd.DataFrame) -> None:
    """Imprime el rango temporal y el tamaño del dataset."""
    print(f"\nDataset: {name}")
    print(f"Filas: {len(dataframe)}")
    print(f"Inicio: {dataframe.index.min()}")
    print(f"Fin: {dataframe.index.max()}")


def print_suite_results(title: str, results: list[dict]) -> None:
    """Muestra resultados de varias estrategias sobre una misma muestra."""
    print(f"\n########## {title} ##########")
    for result in results:
        strategy_name = result["strategy"]
        metrics = {key: value for key, value in result.items() if key != "strategy"}
        print_metrics(strategy_name, metrics)


def build_demo_data_dict(dataframe: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Devuelve una estructura lista para usar con run_all_tests()."""
    return {"SPY_1d": dataframe}


def main() -> None:
    """Ejemplo completo de uso sobre un dataset diario de SPY."""
    csv_path = download_ohlcv(
        symbol=DEFAULT_SYMBOL,
        start=DEFAULT_START,
        end=DEFAULT_END,
        interval="1d",
    )
    dataframe = load_ohlcv(csv_path)

    print(f"CSV usado: {Path(csv_path).resolve()}")
    print_dataset_overview("SPY_1d", dataframe)

    config = BacktestConfig(
        initial_cash=10_000,
        commission=0.001,
        spread=0.0005,
        split_ratio=0.7,
    )

    in_sample, out_of_sample = split_in_sample_out_of_sample(
        dataframe, split_ratio=config.split_ratio
    )

    print_suite_results("IN-SAMPLE", run_strategy_suite(in_sample, config))
    print_suite_results("OUT-OF-SAMPLE", run_strategy_suite(out_of_sample, config))

    print("\n########## RESUMEN MULTI-TEST ##########")
    data_dict = build_demo_data_dict(dataframe)
    summary = run_all_tests(data_dict, config)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
