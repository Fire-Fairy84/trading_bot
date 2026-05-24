"""Tests del runner y generación de reportes."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import run_backtest
from evaluation import BacktestConfig


def test_save_html_reports_creates_reports_dir(
    monkeypatch,
    sample_ohlcv_df: pd.DataFrame,
    tmp_path: Path,
) -> None:
    reports_dir = tmp_path / "nested" / "reports"
    created_targets: list[Path] = []

    class BacktestStub:
        def plot(self, filename: str, open_browser: bool) -> None:
            path = Path(filename)
            path.write_text("html", encoding="utf-8")
            created_targets.append(path)

    def fake_run_strategy(dataframe, strategy_name: str, config: BacktestConfig):
        return BacktestStub(), None, {"strategy": strategy_name}

    monkeypatch.setattr(run_backtest, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(run_backtest, "run_strategy", fake_run_strategy)

    html_paths = run_backtest.save_html_reports(
        "SYNTH_1d",
        sample_ohlcv_df,
        BacktestConfig(),
    )

    assert reports_dir.exists()
    assert len(html_paths) == 8
    assert created_targets == html_paths
    assert all(path.exists() for path in html_paths)


def test_build_data_dict_uses_custom_dataset_name(sample_ohlcv_df: pd.DataFrame) -> None:
    data_dict = run_backtest.build_data_dict("QQQ_1d", sample_ohlcv_df)
    assert list(data_dict) == ["QQQ_1d"]


def test_run_settings_resolves_dataset_name_from_symbol_and_interval() -> None:
    settings = run_backtest.RunSettings(symbol="QQQ", interval="1wk")
    assert settings.resolved_dataset_name == "QQQ_1wk"


def test_load_dataset_uses_custom_symbol_interval_and_dates(
    monkeypatch,
    sample_ohlcv_df: pd.DataFrame,
    tmp_path: Path,
) -> None:
    settings = run_backtest.RunSettings(
        symbol="QQQ",
        interval="1wk",
        start="2020-01-01",
        end="2021-01-01",
    )
    expected_csv_path = tmp_path / "QQQ_1wk.csv"
    download_calls: list[dict[str, str]] = []

    monkeypatch.setattr(run_backtest.RunSettings, "local_csv_path", property(lambda self: expected_csv_path))

    def fake_download_ohlcv(symbol: str, start: str, end: str, interval: str):
        download_calls.append(
            {"symbol": symbol, "start": start, "end": end, "interval": interval}
        )
        return expected_csv_path

    monkeypatch.setattr(run_backtest, "download_ohlcv", fake_download_ohlcv)
    monkeypatch.setattr(run_backtest, "load_ohlcv", lambda csv_path: sample_ohlcv_df)

    dataframe, csv_path = run_backtest.load_dataset(settings)

    assert dataframe.equals(sample_ohlcv_df)
    assert csv_path == expected_csv_path
    assert download_calls == [
        {
            "symbol": "QQQ",
            "start": "2020-01-01",
            "end": "2021-01-01",
            "interval": "1wk",
        }
    ]
