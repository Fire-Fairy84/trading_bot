"""Script principal para descargar datos y ejecutar el backtest."""

from pathlib import Path

from backtesting import Backtest

from load_data import download_ohlcv, load_ohlcv, split_in_sample_out_of_sample
from strategy import SwingSmaRsiStrategy


DEFAULT_SYMBOL = "SPY"
DEFAULT_START = "2015-01-01"
DEFAULT_END = "2025-01-01"
COMMISSION = 0.001
SPREAD = 0.0005
INITIAL_CASH = 10_000


def build_backtest(dataframe):
    """Crea un objeto Backtest con supuestos explícitos de costes."""
    return Backtest(
        dataframe,
        SwingSmaRsiStrategy,
        cash=INITIAL_CASH,
        commission=COMMISSION,
        spread=SPREAD,
        exclusive_orders=True,
        trade_on_close=False,
    )


def print_summary(title: str, stats) -> None:
    """Imprime un resumen corto con métricas básicas."""
    print(f"\n=== {title} ===")
    print(f"Start: {stats['Start']}")
    print(f"End: {stats['End']}")
    print(f"Return [%]: {stats['Return [%]']:.2f}")
    print(f"Return (Ann.) [%]: {stats['Return (Ann.) [%]']:.2f}")
    print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
    print(f"Max. Drawdown [%]: {stats['Max. Drawdown [%]']:.2f}")
    print(f"Win Rate [%]: {stats['Win Rate [%]']:.2f}")
    print(f"Profit Factor: {stats['Profit Factor']:.2f}")
    print(f"# Trades: {int(stats['# Trades'])}")


def main() -> None:
    """Descarga datos, separa muestras y ejecuta dos backtests."""
    csv_path = download_ohlcv(
        symbol=DEFAULT_SYMBOL,
        start=DEFAULT_START,
        end=DEFAULT_END,
        interval="1d",
    )

    dataframe = load_ohlcv(csv_path)
    in_sample, out_of_sample = split_in_sample_out_of_sample(dataframe, split_ratio=0.7)

    print(f"CSV usado: {Path(csv_path).resolve()}")
    print(f"Filas totales: {len(dataframe)}")
    print(
        f"in-sample: {in_sample.index.min().date()} -> {in_sample.index.max().date()} "
        f"({len(in_sample)} filas)"
    )
    print(
        f"out-of-sample: {out_of_sample.index.min().date()} -> "
        f"{out_of_sample.index.max().date()} ({len(out_of_sample)} filas)"
    )

    in_sample_bt = build_backtest(in_sample)
    in_sample_stats = in_sample_bt.run()
    print_summary("IN-SAMPLE", in_sample_stats)

    out_of_sample_bt = build_backtest(out_of_sample)
    out_of_sample_stats = out_of_sample_bt.run()
    print_summary("OUT-OF-SAMPLE", out_of_sample_stats)

    try:
        reports_dir = Path(__file__).resolve().parent.parent / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        in_sample_bt.plot(filename=str(reports_dir / "in_sample_backtest.html"), open_browser=False)
        out_of_sample_bt.plot(
            filename=str(reports_dir / "out_of_sample_backtest.html"),
            open_browser=False,
        )
        print("\nSe generaron gráficos HTML en la carpeta reports/.")
    except Exception as error:
        print(f"\nNo se pudieron generar los gráficos HTML: {error}")


if __name__ == "__main__":
    main()
