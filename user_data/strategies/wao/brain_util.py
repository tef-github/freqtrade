import threading
import watchdog
import os
import time
from wao.brain_config import BrainConfig
from wao._429_watcher import _429_Watcher
from wao.error_watcher import Error_Watcher
import pickle

from execution.config import Config
from execution.system import System
from execution.system_core import RomeoExitPriceType
from commons.backtest_signal import BacktestSignal


def write_to_backtest_table(timestamp, coin, dup, type):
    print("STEP [1]++++++++++++++++++++++++++++++++++++" + ", write_to_backtest_table")
    BrainConfig.BACKTEST_SIGNAL_LIST.append(BacktestSignal(BrainConfig.BRAIN, coin, type,
                                                           Config.SYSTEM_SS_TIMEOUT_HOURS, dup, timestamp=timestamp))
    pickle.dump(BrainConfig.BACKTEST_SIGNAL_LIST, open(BrainConfig.BACKTEST_SIGNAL_LIST_PICKLE_FILE_PATH, 'wb'))


def perform_execute_buy(coin, dup, execution_index):
    is_test_mode = False
    if BrainConfig.MODE == Config.MODE_TEST:
        is_test_mode = True
    elif BrainConfig.MODE == Config.MODE_PROD:
        is_test_mode = False

    Config.COIN = coin
    Config.SYSTEM_D_UP_PERCENTAGE = dup

    system = System.instance(is_test_mode, True)
    BrainConfig.SYSTEM_POOL[coin] = system
    system.start(execution_index)


def perform_execute_sell(coin, sell_reason):
    if Config.IS_SS_ENABLED:
        system = BrainConfig.SYSTEM_POOL.get(coin)
        if system is not None:
            system.perform_sell_signal(RomeoExitPriceType.SS, sell_reason=sell_reason)


def perform_create_429_watcher():
    print("perform_create_429_watcher: watching:- " + str(BrainConfig._429_DIRECTORY))
    event_handler = _429_Watcher()
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=BrainConfig._429_DIRECTORY, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def perform_create_error_watcher(notifier):
    print("perform_create_error_watcher: watching:- " + str(BrainConfig._WAO_LOGS_DIRECTORY))
    event_handler = Error_Watcher(notifier)
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=BrainConfig._WAO_LOGS_DIRECTORY, recursive=True)
    # Start the observer
    observer.start()
    try:
        while True:
            # Set the thread sleep time
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def create_watchers(notifier):
    if Config.ENABLE_429_SOLUTION:
        __create_429_directory()
        __create_429_watcher()
    if BrainConfig.IS_ERROR_WATCHER_ENABLED:
        __create_error_watcher(notifier)


def clear_cumulative_value():
    # delete cumulative file
    _delete_file(BrainConfig.CUMULATIVE_PROFIT_FILE_PATH)
    _delete_file(BrainConfig.CUMULATIVE_PROFIT_BINANCE_FILE_PATH)
    _delete_file(BrainConfig.INITIAL_ACCOUNT_BALANCE_BINANCE_FILE_PATH)


def _delete_file(file_name):
    if os.path.isfile(file_name):
        os.remove(file_name)


def create_initial_account_balance_binance_file():
    file_path = BrainConfig.INITIAL_ACCOUNT_BALANCE_BINANCE_FILE_PATH
    if not os.path.exists(file_path):
        with open(file_path, 'w+') as file:
            file.write("")
        file.close()


def __create_429_directory():
    print("create_429_directory:..." + BrainConfig._429_DIRECTORY + "...")
    if not os.path.exists(BrainConfig._429_DIRECTORY):
        os.mkdir(BrainConfig._429_DIRECTORY)


def __create_error_watcher(notifier):
    threading.Thread(target=perform_create_error_watcher, args=(notifier,)).start()


def __create_429_watcher():
    threading.Thread(target=perform_create_429_watcher).start()


def delete_backtest_table_file():
    file_name = BrainConfig.BACKTEST_SIGNAL_LIST_PICKLE_FILE_PATH
    if os.path.isfile(file_name):
        os.remove(file_name)


def is_romeo_alive(coin):
    return BrainConfig.SYSTEM_POOL.get(coin) is not None


def remove_from_pool(coin):
    if is_romeo_alive(coin):
        del BrainConfig.SYSTEM_POOL[coin]
