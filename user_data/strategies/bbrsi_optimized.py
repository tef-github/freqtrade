# --- Do not remove these libs ---
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import numpy  # noqa
from wao.wao_strategy import WAOStrategy


class bbrsi_optimized(WAOStrategy):
    brain = "Freq_bbrsi_scalp"

    def __init__(self, config: dict):
        self.coin = str(config.get('pairs')[0]).split('/')[0]
        if self.coin == 'BTC' or self.coin == 'ADA':
            self.brain = "Freq_bbrsi_scalp_ada_btc"
        super().__init__(config, self.brain, 8, 0.15)

    timeframe = '5m'

    # ROI table:
    minimal_roi = {
        "190": 0.005,  # Exit after 500 minutes there is at least 0.5% profit
        "175": 0.006,  # Exit after 500 minutes there is at least 0.5% profit
        "160": 0.007,  # Exit after 40 minutes if there is at least 1% profit
        "145": 0.008,  # Exit after 40 minutes if there is at least 1% profit
        "130": 0.009,  # Exit after 40 minutes if there is at least 1% profit
        "115": 0.010,  # Exit after 20 minutes if there is at least 1.5% profit
        "100": 0.011,  # Exit after 20 minutes if there is at least 1.5% profit
        "85": 0.012,  # Exit after 20 minutes if there is at least 1.5% profit
        "60": 0.013,  # Exit after 20 minutes if there is at least 1.5% profit
        "45": 0.014,  # Exit immediately if there is at least 2% profit
        "30": 0.016,  # Exit immediately if there is at least 2% profit
        "15": 0.018,  # Exit immediately if there is at least 2% profit
        "0": 0.020,  # Exit immediately if there is at least 2% profit
    }

    # Stoploss:
    stoploss = -0.02

    # Trailing stop:
    trailing_stop = True  # value loaded from strategy
    trailing_stop_positive = 0.237  # value loaded from strategy
    trailing_stop_positive_offset = 0.245  # value loaded from strategy
    trailing_only_offset_is_reached = True  # value loaded from strategy

    # run "populate_indicators" only for new candle
    process_only_new_candles = False

    # Experimental settings (configuration will overide these if set)
    use_sell_signal = True
    sell_profit_only = True
    ignore_roi_if_buy_signal = False

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
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        """

        # Stoch
        # stoch = ta.STOCH(dataframe)
        # dataframe['slowk'] = stoch['slowk']

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe)

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
                    (qtpylib.crossed_above(dataframe['close'], dataframe['bb_lowerband'])) &
                    (dataframe['rsi'] < 50)
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
                    (dataframe['close'] > dataframe['bb_upperband']) |
                    (dataframe['rsi'] > 60)
            ),
            'sell'] = 1
        return dataframe