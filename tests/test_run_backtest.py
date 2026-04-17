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
