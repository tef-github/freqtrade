# --- Do not remove these libs ---
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import numpy  # noqa
# from wao.wao_strategy import WAOStrategy
# from wao.brain_config import BrainConfig
from freqtrade.strategy import IStrategy


class bb_scalp_15m_pure(IStrategy):
    timeframe = '15m'

    # minimal_roi = {
    #     "80": 0.006,  # Exit after 20 minutes if there is at least 1.5% profit
    #     "70": 0.007,  # Exit after 20 minutes if there is at least 1.5% profit
    #     "60": 0.008,  # Exit immediately if there is at least 2% profit
    #     "40": 0.010,  # Exit immediately if there is at least 2% profit
    #     "20": 0.014,  # Exit immediately if there is at least 2% profit
    #     "0": 0.018,  # Exit immediately if there is at least 2% profit
    # }

    minimal_roi = {
        "60":  0.01,
        "30":  0.03,
        "20":  0.04,
        "0":  0.05
    }

    # Stoploss:
    stoploss = -0.01

    # Trailing stop:
    trailing_stop = False
    trailing_stop_positive = 0.089
    trailing_stop_positive_offset = 0.11
    trailing_only_offset_is_reached = False

    # run "populate_indicators" only for new candle
    process_only_new_candles = False

    # Experimental settings (configuration will overide these if set)
    use_exit_signal = True
    exit_profit_only = True
    ignore_roi_if_entry_signal = True

    # Optional order type mapping.
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'trailing_stop_loss': 'limit',
        'stoploss': 'limit',
        'stoploss_on_exchange': False
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame
        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your refined-strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        """

        # Stoch
        # stoch = ta.STOCH(dataframe)
        # dataframe['slowk'] = stoch['slowk']

        # RSI
        # dataframe['rsi'] = ta.RSI(dataframe)
        # SMA
        # dataframe['sma_200'] = ta.SMA(dataframe, timeperiod=200)
        # EMA
        # dataframe['ema_9'] = ta.EMA(dataframe, timeperiod=9)

        # MACD
        # macd = ta.MACD(dataframe)
        # dataframe['macd'] = macd['macd']
        # dataframe['macdsignal'] = macd['macdsignal']
        # dataframe['macdhist'] = macd['macdhist']

        # Inverse Fisher transform on RSI, values [-1.0, 1.0] (https://goo.gl/2JGGoy)
        # rsi = 0.1 * (dataframe['rsi'] - 50)
        # dataframe['fisher_rsi'] = (numpy.exp(2 * rsi) - 1) / (numpy.exp(2 * rsi) + 1)

        # Bollinger bands
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        # dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']

        # SAR Parabol
        # dataframe['sar'] = ta.SAR(dataframe)

        # Hammer: values [0, 100]
        # dataframe['CDLHAMMER'] = ta.CDLHAMMER(dataframe)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe['close'], dataframe['bb_lowerband'])
                # & (dataframe['rsi'] < 50)
                # & (dataframe['ema_9'] > dataframe['sma_200'])
                # & (dataframe['macdhist'] > -0.08)
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['close'] > dataframe['bb_upperband'])
                # | (dataframe['rsi'] > 60)
                # | (qtpylib.crossed_below(dataframe['ema_9'], dataframe['sma_200']))

            ),
            'sell'] = 1
        return dataframe