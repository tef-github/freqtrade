from wao.brain_util import perform_execute_buy, perform_execute_sell, write_to_backtest_table, clear_cumulative_value, create_initial_account_balance_binance_file, is_romeo_alive, remove_from_pool
import threading
from wao.brain_config import BrainConfig
from wao.brain_util import create_watchers
from wao.notifier import send_start_deliminator_message
import sys
import os

sys.path.append(BrainConfig.EXECUTION_PATH)
from config import Config


class WAOStrategyController:

    def __init__(self, brain, time_out_hours, dup):
        self.brain = brain
        self.time_out_hours = time_out_hours
        self.dup = dup
        print("WAOStrategyController: __init__: is_backtest=" + str(BrainConfig.IS_BACKTEST))
        create_watchers()
        clear_cumulative_value()
        create_initial_account_balance_binance_file()
        if BrainConfig.IS_BACKTEST:
            send_start_deliminator_message(self.brain,
                                           BrainConfig.BACKTEST_MONTH_LIST[
                                               BrainConfig.BACKTEST_DATA_CLEANER_MONTH_INDEX],
                                           BrainConfig.BACKTEST_DATA_CLEANER_YEAR)

    def on_buy_signal(self, current_time, coin):
        print("WAOStrategyController: on_buy_signal: current_time=" + str(current_time) + ", coin=" + str(coin) +
              ", brain=" + str(self.brain))

        if is_romeo_alive(coin):
            print("WAOStrategyController: on_buy_signal: warning: alive romeo detected: ignoring buy_signal!")
            return

        if BrainConfig.IS_BACKTEST:
            write_to_backtest_table(current_time, coin, self.brain, self.time_out_hours, self.dup, "buy")
        else:
            self.__buy_execute(coin)

    def on_sell_signal(self, sell_reason, current_time, coin):
        print("WAOStrategyController: on_sell_signal: sell_reason=" + str(sell_reason) + ", current_time=" + str(
            current_time) + ", coin=" + str(coin) + ", brain=" + str(self.brain))
        if BrainConfig.IS_BACKTEST:
            write_to_backtest_table(current_time, coin, self.brain, self.time_out_hours, self.dup, "sell")
        else:
            perform_execute_sell(coin)
            remove_from_pool(coin)

    def __buy_execute(self, coin):
        if Config.IS_PARALLEL_EXECUTION:
            threading.Thread(target=perform_execute_buy,
                             args=(coin, self.brain, self.time_out_hours, self.dup)).start()
        else:
            perform_execute_buy(coin, self.brain, self.time_out_hours, self.dup)

    @Config.bus.on(Config.EVENT_BUS_EXECUTION_SELF_COMPLETE)
    def on_execution_self_complete(coin):
        print("on_execution_self_complete: " + coin)
        remove_from_pool(coin)


