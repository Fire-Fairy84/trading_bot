"""Estrategias e indicadores reutilizables para backtesting.py."""

from __future__ import annotations

from math import floor

import numpy as np
import pandas as pd
from backtesting import Strategy


def sma(values, period: int) -> pd.Series:
    """Simple Moving Average."""
    return pd.Series(values).rolling(period).mean()


def atr(high, low, close, period: int = 14) -> pd.Series:
    """Average True Range con suavizado tipo Wilder."""
    high_series = pd.Series(high)
    low_series = pd.Series(low)
    close_series = pd.Series(close)
    previous_close = close_series.shift(1)

    true_range = pd.concat(
        [
            high_series - low_series,
            (high_series - previous_close).abs(),
            (low_series - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return true_range.ewm(alpha=1 / period, adjust=False).mean()


def rsi_wilder(values, period: int = 14) -> pd.Series:
    """RSI con suavizado de Wilder.

    Esta implementación es más robusta que una versión manual muy básica,
    y evita divisiones problemáticas cuando las pérdidas medias son cero.
    """
    close = pd.Series(values)
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    avg_gain = gains.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / period, adjust=False).mean()

    relative_strength = avg_gain / avg_loss.replace(0, np.nan)
    rsi_values = 100 - (100 / (1 + relative_strength))
    rsi_values = rsi_values.where(avg_loss != 0, 100)
    rsi_values = rsi_values.where(avg_gain != 0, 0)
    return rsi_values.fillna(50)


def crossed_above_level(series, level: float) -> bool:
    """Detecta cruce alcista de una serie contra un nivel fijo."""
    if len(series) < 2 or np.isnan(series[-1]) or np.isnan(series[-2]):
        return False
    return series[-2] <= level < series[-1]


def crossed_above_series(series_a, series_b) -> bool:
    """Detecta cruce alcista entre dos series usando solo barras confirmadas."""
    if len(series_a) < 2 or len(series_b) < 2:
        return False
    if any(np.isnan(value) for value in [series_a[-2], series_a[-1], series_b[-2], series_b[-1]]):
        return False
    return series_a[-2] <= series_b[-2] and series_a[-1] > series_b[-1]


def crossed_below_series(series_a, series_b) -> bool:
    """Detecta cruce bajista entre dos series usando solo barras confirmadas."""
    if len(series_a) < 2 or len(series_b) < 2:
        return False
    if any(np.isnan(value) for value in [series_a[-2], series_a[-1], series_b[-2], series_b[-1]]):
        return False
    return series_a[-2] >= series_b[-2] and series_a[-1] < series_b[-1]


class BuyAndHoldStrategy(Strategy):
    """Benchmark básico: compra una vez y mantiene."""

    entry_fraction = 0.99

    def init(self) -> None:
        """No necesita indicadores, pero Strategy exige init()."""

    def next(self) -> None:
        if not self.position:
            self.buy(size=self.entry_fraction)


class SmaCrossBenchmarkStrategy(Strategy):
    """Benchmark long-only con cruce simple de medias."""

    fast_period = 50
    slow_period = 200
    entry_fraction = 0.99

    def init(self) -> None:
        self.sma_fast = self.I(sma, self.data.Close, self.fast_period)
        self.sma_slow = self.I(sma, self.data.Close, self.slow_period)

    def next(self) -> None:
        if not self.position and crossed_above_series(self.sma_fast, self.sma_slow):
            self.buy(size=self.entry_fraction)
            return

        if self.position and crossed_below_series(self.sma_fast, self.sma_slow):
            self.position.close()


class RiskManagedSwingStrategy(Strategy):
    """Estrategia swing con stop configurable y sizing por riesgo.

    La idea sigue siendo simple:
    - filtro de tendencia con SMA 50 > SMA 200
    - recuperación de momentum con RSI
    - salida por pérdida de tendencia o momentum
    - stop loss y tamaño de posición calculados con criterio de riesgo
    """

    fast_period = 50
    slow_period = 200
    rsi_period = 14
    atr_period = 14

    rsi_entry = 55
    rsi_exit = 45

    stop_mode = "atr"  # "atr" o "percent"
    stop_loss_pct = 0.08
    atr_multiple = 2.5
    use_rsi_exit = True
    use_trailing_stop = False
    trailing_atr_multiple = 3.0

    risk_per_trade = 0.01
    entry_slippage = 0.0005
    min_position_size = 1

    def init(self) -> None:
        # Guardamos el mejor cierre desde la entrada para poder mover
        # un trailing stop solo en dirección favorable.
        self.highest_close_since_entry: float | None = None
        self.sma_fast = self.I(sma, self.data.Close, self.fast_period)
        self.sma_slow = self.I(sma, self.data.Close, self.slow_period)
        self.rsi_value = self.I(rsi_wilder, self.data.Close, self.rsi_period)
        self.atr_value = self.I(
            atr, self.data.High, self.data.Low, self.data.Close, self.atr_period
        )

    def _current_stop_price(self, estimated_entry: float) -> float | None:
        """Devuelve el stop inicial según el modo configurado."""
        if self.stop_mode == "percent":
            return estimated_entry * (1 - self.stop_loss_pct)

        if self.stop_mode == "atr":
            current_atr = self.atr_value[-1]
            if np.isnan(current_atr) or current_atr <= 0:
                return None
            return estimated_entry - (current_atr * self.atr_multiple)

        raise ValueError("stop_mode debe ser 'percent' o 'atr'.")

    def _entry_signal_is_ready(self, price: float, sma_fast_now: float, sma_slow_now: float) -> bool:
        """Mantiene la condición de entrada legible y fácil de modificar."""
        uptrend = sma_fast_now > sma_slow_now
        price_above_fast_sma = price > sma_fast_now
        momentum_recovered = crossed_above_level(self.rsi_value, self.rsi_entry)
        return uptrend and price_above_fast_sma and momentum_recovered

    def _risk_based_position_size(self, estimated_entry: float, stop_price: float) -> int:
        """Calcula unidades máximas arriesgando como mucho el 1% del equity.

        Formula:
        - riesgo monetario permitido = equity * risk_per_trade
        - riesgo por unidad = entry - stop
        - size = riesgo permitido / riesgo por unidad
        """
        risk_per_unit = estimated_entry - stop_price
        if risk_per_unit <= 0:
            return 0

        equity = float(self.equity)
        risk_budget = equity * self.risk_per_trade
        size_from_risk = floor(risk_budget / risk_per_unit)

        # También limitamos por capital disponible para no pedir más unidades
        # de las que podríamos pagar con el efectivo del backtest.
        affordable_size = floor(equity / estimated_entry)
        size = min(size_from_risk, affordable_size)

        if size < self.min_position_size:
            return 0

        return size

    def _update_trailing_stop(self, price: float) -> None:
        """Ajusta un trailing stop sencillo basado en ATR.

        Idea educativa:
        - no intenta adivinar el techo
        - solo va subiendo el stop si el precio nos favorece
        - nunca lo baja, para no ampliar el riesgo una vez dentro
        """
        if not self.position or not self.use_trailing_stop or self.stop_mode != "atr":
            return

        current_atr = self.atr_value[-1]
        if np.isnan(current_atr) or current_atr <= 0:
            return

        if self.highest_close_since_entry is None:
            self.highest_close_since_entry = price
        else:
            self.highest_close_since_entry = max(self.highest_close_since_entry, price)

        new_stop = self.highest_close_since_entry - (current_atr * self.trailing_atr_multiple)
        open_trades = list(self.trades)
        if not open_trades:
            return

        current_stop = open_trades[0].sl
        if current_stop is None or new_stop > current_stop:
            for trade in open_trades:
                trade.sl = new_stop

    def _should_exit_position(self, price: float, sma_fast_now: float, rsi_now: float) -> bool:
        """Separa la lógica de salida para comparar variantes con claridad."""
        trend_lost = price < sma_fast_now
        momentum_lost = self.use_rsi_exit and rsi_now < self.rsi_exit
        return trend_lost or momentum_lost

    def next(self) -> None:
        price = float(self.data.Close[-1])
        sma_fast_now = self.sma_fast[-1]
        sma_slow_now = self.sma_slow[-1]
        rsi_now = self.rsi_value[-1]

        if any(np.isnan(value) for value in [sma_fast_now, sma_slow_now, rsi_now]):
            return

        if not self.position:
            if not self._entry_signal_is_ready(price, sma_fast_now, sma_slow_now):
                return

            estimated_entry = price * (1 + self.entry_slippage)
            stop_price = self._current_stop_price(estimated_entry)
            if stop_price is None or stop_price >= estimated_entry:
                return

            size = self._risk_based_position_size(estimated_entry, stop_price)
            if size <= 0:
                return

            self.buy(size=size, sl=stop_price)
            self.highest_close_since_entry = price
            return

        self._update_trailing_stop(price)

        if self._should_exit_position(price, sma_fast_now, rsi_now):
            self.position.close()
            self.highest_close_since_entry = None


class FlexibleEntrySwingStrategy(RiskManagedSwingStrategy):
    """Versión con entrada un poco menos estricta.

    Pasamos de RSI 55 a 52 para aceptar recuperaciones de momentum
    algo antes. Eso suele aumentar el número de señales.
    """

    rsi_entry = 52


class CalmerExitSwingStrategy(RiskManagedSwingStrategy):
    """Versión con salida menos agresiva.

    En vez de salir por RSI "demasiado pronto", dejamos que el stop ATR
    y la pérdida de tendencia hagan más trabajo. Añadimos además un
    trailing stop sencillo para proteger parte del avance.
    """

    use_rsi_exit = False
    use_trailing_stop = True
    trailing_atr_multiple = 3.0


class WiderAtrStopSwingStrategy(RiskManagedSwingStrategy):
    """Versión con stop ATR más amplio para evitar ruido normal."""

    atr_multiple = 3.0


class PercentStopSwingStrategy(RiskManagedSwingStrategy):
    """Alternativa opcional con stop porcentual fijo.

    No se incluye en la comparativa principal para evitar demasiadas
    variantes, pero queda disponible para aprendizaje.
    """

    stop_mode = "percent"
    stop_loss_pct = 0.10
