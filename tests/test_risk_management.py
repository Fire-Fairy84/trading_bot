"""Tests de sizing y cálculo de stop."""

from __future__ import annotations

import pytest

from strategy import RiskManagedSwingStrategy


class BrokerStub:
    """Stub mínimo para exponer equity como lo hace backtesting.py."""

    def __init__(self, equity: float) -> None:
        self.equity = equity


def build_strategy_stub(equity: float = 10_000) -> RiskManagedSwingStrategy:
    """Crea una instancia mínima para probar helpers sin correr un backtest."""
    strategy = RiskManagedSwingStrategy.__new__(RiskManagedSwingStrategy)
    strategy.stop_mode = "atr"
    strategy.stop_loss_pct = 0.08
    strategy.atr_multiple = 2.5
    strategy.atr_value = [1.5]
    strategy.risk_per_trade = 0.01
    strategy.min_position_size = 1
    strategy._broker = BrokerStub(equity=equity)
    return strategy


def test_percent_stop_loss_is_calculated_from_entry() -> None:
    strategy = build_strategy_stub()
    strategy.stop_mode = "percent"
    stop_price = strategy._current_stop_price(100)
    assert stop_price == pytest.approx(92.0)


def test_atr_stop_loss_uses_atr_multiple() -> None:
    strategy = build_strategy_stub()
    stop_price = strategy._current_stop_price(100)
    assert stop_price == pytest.approx(96.25)


def test_risk_based_position_size_uses_risk_budget_and_affordability() -> None:
    strategy = build_strategy_stub()
    size = strategy._risk_based_position_size(estimated_entry=100, stop_price=95)
    assert size == 20


def test_risk_based_position_size_returns_zero_when_risk_is_invalid() -> None:
    strategy = build_strategy_stub()
    size = strategy._risk_based_position_size(estimated_entry=100, stop_price=100)
    assert size == 0


def test_risk_based_position_size_returns_zero_when_below_minimum() -> None:
    strategy = build_strategy_stub(equity=300)
    strategy.min_position_size = 5
    size = strategy._risk_based_position_size(estimated_entry=100, stop_price=98)
    assert size == 0
