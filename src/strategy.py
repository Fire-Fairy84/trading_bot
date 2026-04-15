"""Estrategia swing simple para aprender backtesting.py."""

import pandas as pd
from backtesting import Strategy


def sma(values, period: int) -> pd.Series:
    """Simple Moving Average.

    SMA es una media simple de los últimos N cierres.
    """
    return pd.Series(values).rolling(period).mean()


def rsi(values, period: int = 14) -> pd.Series:
    """Relative Strength Index.

    RSI mide el impulso del precio en una escala aproximada de 0 a 100.
    """
    close = pd.Series(values)
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    average_gain = gains.ewm(alpha=1 / period, adjust=False).mean()
    average_loss = losses.ewm(alpha=1 / period, adjust=False).mean()

    rs = average_gain / average_loss.replace(0, pd.NA)
    rsi_series = 100 - (100 / (1 + rs))
    return rsi_series.fillna(50)


class SwingSmaRsiStrategy(Strategy):
    """Estrategia long-only con filtro de tendencia y filtro de momentum.

    Reglas pedagógicas:
    - Tendencia principal: SMA 50 > SMA 200
    - Entrada: Close > SMA 50 y RSI cruza por encima de 55
    - Salida: Close < SMA 50 o RSI cae por debajo de 45
    """

    fast_period = 50
    slow_period = 200
    rsi_period = 14
    rsi_entry = 55
    rsi_exit = 45

    def init(self) -> None:
        """Declara indicadores para que backtesting.py los calcule una vez."""
        self.sma_fast = self.I(sma, self.data.Close, self.fast_period)
        self.sma_slow = self.I(sma, self.data.Close, self.slow_period)
        self.rsi_value = self.I(rsi, self.data.Close, self.rsi_period)

    def next(self) -> None:
        """Se ejecuta en cada vela nueva."""
        price = self.data.Close[-1]
        sma_fast_now = self.sma_fast[-1]
        sma_slow_now = self.sma_slow[-1]
        rsi_now = self.rsi_value[-1]
        rsi_prev = self.rsi_value[-2]

        uptrend = sma_fast_now > sma_slow_now
        pullback_recovered = rsi_prev <= self.rsi_entry and rsi_now > self.rsi_entry

        if not self.position:
            if uptrend and price > sma_fast_now and pullback_recovered:
                self.buy()
            return

        exit_by_trend_loss = price < sma_fast_now
        exit_by_momentum_loss = rsi_now < self.rsi_exit

        if exit_by_trend_loss or exit_by_momentum_loss:
            self.position.close()
