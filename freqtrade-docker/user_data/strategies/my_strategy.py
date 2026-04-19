from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class MiEstrategia(IStrategy):
    """
    Estrategia base educativa para el entorno Freqtrade.

    Esta version se queda como default porque en el backtesting inicial
    ha sido mas estable que la traduccion directa de la fase B.
    Su objetivo no es ser una estrategia final, sino una base clara y
    facil de depurar mientras aprendes el flujo completo de Freqtrade.
    """

    INTERFACE_VERSION = 3

    timeframe = "1h"
    can_short = False

    minimal_roi = {
        "0": 0.04,
        "60": 0.02,
        "180": 0.01,
    }

    stoploss = -0.10
    startup_candle_count = 30

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=12)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=26)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["ema_fast"] > dataframe["ema_slow"])
                & (dataframe["rsi"] > 55)
                & (dataframe["volume"] > 0)
            ),
            ["enter_long", "enter_tag"],
        ] = (1, "ema_rsi_momentum")

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["ema_fast"] < dataframe["ema_slow"])
                | (dataframe["rsi"] < 45)
            ),
            ["exit_long", "exit_tag"],
        ] = (1, "ema_or_rsi_lost")

        return dataframe


class MiEstrategiaFaseB(IStrategy):
    """
    Traduccion sencilla de la logica swing de la fase B.

    Ideas que porta:
    - tendencia principal con SMA 50 > SMA 200
    - precio por encima de la SMA 50
    - entrada cuando RSI recupera momentum
    - salida cuando la tendencia tactica se debilita

    Ojo: en BTC/ETH a 1h esta version no ha mejorado a la base, lo cual
    es una leccion util. Una idea razonable en SPY 1d no se traslada
    automaticamente a otro mercado y otro timeframe.
    """

    INTERFACE_VERSION = 3

    timeframe = "1h"
    can_short = False

    # Mantenemos un ROI muy alto para que el backtest dependa sobre todo
    # de la salida por senal y del stoploss.
    minimal_roi = {
        "0": 10.0
    }

    stoploss = -0.08
    startup_candle_count = 220

    use_exit_signal = True
    exit_profit_only = False
    process_only_new_candles = True

    rsi_entry_threshold = 55
    rsi_exit_threshold = 45

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["sma_fast"] = ta.SMA(dataframe, timeperiod=50)
        dataframe["sma_slow"] = ta.SMA(dataframe, timeperiod=200)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        rsi_cross_up = (
            (dataframe["rsi"] > self.rsi_entry_threshold)
            & (dataframe["rsi"].shift(1) <= self.rsi_entry_threshold)
        )

        dataframe.loc[
            (
                (dataframe["sma_fast"] > dataframe["sma_slow"])
                & (dataframe["close"] > dataframe["sma_fast"])
                & rsi_cross_up
                & (dataframe["volume"] > 0)
            ),
            ["enter_long", "enter_tag"],
        ] = (1, "trend_rsi_recovery")

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["close"] < dataframe["sma_fast"])
                | (dataframe["rsi"] < self.rsi_exit_threshold)
            ),
            ["exit_long", "exit_tag"],
        ] = (1, "trend_or_momentum_lost")

        return dataframe
