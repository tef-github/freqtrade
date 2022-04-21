import sys
import threading
import watchdog
import os
import time
import datetime
from wao.brain_config import BrainConfig
from wao._429_watcher import _429_Watcher
from wao.backtest_execution import BacktestExecution

sys.path.append(BrainConfig.EXECUTION_PATH)
from config import Config
from romeo import Romeo, RomeoExitPriceType
import pickle


def is_execution_state_open():
    return not os.path.isfile(Config.BACKTEST_EXECUTION_FINISHED_FILE_PATH)


def clear_execution_state():
    filename = Config.BACKTEST_EXECUTION_FINISHED_FILE_PATH
    if os.path.isfile(filename):
        os.remove(filename)


def write_to_backtest_table(timestamp, coin, brain, time_out_hours, type):
    print("STEP [1]++++++++++++++++++++++++++++++++++++" + ", write_to_backtest_table")
    BrainConfig.BACKTEST_EXECUTION_LIST.append(BacktestExecution(brain, coin, type, time_out_hours, timestamp=timestamp))
    print(BrainConfig.BACKTEST_EXECUTION_LIST)
    pickle.dump(str(BrainConfig.BACKTEST_EXECUTION_LIST), open(BrainConfig.BACKTEST_EXECUTION_LIST_FILE_PATH, 'w'))


def perform_execute_buy(coin, brain, romeo_pool, time_out_hours):
    is_test_mode = False
    if BrainConfig.MODE == Config.MODE_TEST:
        is_test_mode = True
    elif BrainConfig.MODE == Config.MODE_PROD:
        is_test_mode = False

    Config.COIN = coin
    Config.BRAIN = brain
    Config.ROMEO_SS_TIMEOUT_HOURS = time_out_hours

    romeo = Romeo.instance(is_test_mode, True)
    romeo_pool[coin] = romeo
    romeo.start()


def perform_execute_sell(coin, romeo_pool):
    if Config.IS_SS_ENABLED:
        romeo = romeo_pool.get(coin)
        if romeo is not None:
            romeo.perform_sell_signal(RomeoExitPriceType.SS)


def perform_back_test_sell(date_time):
    if Config.IS_SS_ENABLED:
        date = str(date_time).replace(" ", ", ")
        Config.BACKTEST_SELL_SIGNAL_TIMESTAMP = __get_unix_timestamp(date.split("+", 1)[0])


def perform_back_test_buy(date_time, coin, brain, time_out_hours):
    Config.COIN = coin
    Config.BRAIN = brain
    Config.ROMEO_SS_TIMEOUT_HOURS = time_out_hours
    Config.ROMEO_D_UP_PERCENTAGE = float(BrainConfig.BACKTEST_DUP)
    Config.ROMEO_D_UP_MAX = int(BrainConfig.BACKTEST_MAX_COUNT_DUP)
    date = str(date_time).replace(" ", ", ")
    Config.BACKTEST_BUY_SIGNAL_TIMESTAMP = __get_unix_timestamp(date.split("+", 1)[0])
    Config.BACKTEST_MONTH_INDEX = __get_month_from_timestamp()
    Config.BACKTEST_YEAR = __get_year_from_timestamp()
    print("_perform_back_test: Config.BACKTEST_BUY_SIGNAL_TIMESTAMP = " + str(
        Config.BACKTEST_BUY_SIGNAL_TIMESTAMP) + " Config.BACKTEST_MONTH_INDEX = " + str(
        Config.BACKTEST_MONTH_INDEX) + " Config.COIN = " + str(
        Config.COIN) + " Config.BRAIN = " + str(
        Config.BRAIN) + " Config.ROMEO_D_UP_PERCENTAGE = " + str(
        Config.ROMEO_D_UP_PERCENTAGE) + " Config.ROMEO_D_UP_MAX = " + str(
        Config.ROMEO_D_UP_MAX))

    romeo = Romeo.instance(True, True)
    romeo.start()


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


def setup_429():
    if Config.ENABLE_429_SOLUTION:
        __create_429_directory()
        __create_429_watcher()


def __create_429_directory():
    print("create_429_directory:..." + BrainConfig._429_DIRECTORY + "...")
    if not os.path.exists(BrainConfig._429_DIRECTORY):
        os.mkdir(BrainConfig._429_DIRECTORY)


def __create_429_watcher():
    threading.Thread(target=perform_create_429_watcher).start()


def __get_month_from_timestamp():
    print("__get_month_from_timestamp")
    date = str(time.strftime("%Y-%m-%d", time.localtime(Config.BACKTEST_BUY_SIGNAL_TIMESTAMP)))
    date = datetime.datetime.strptime(str(date), "%Y-%m-%d")
    return date.month - 1 if date.month < 12 else 0


def __get_year_from_timestamp():
    print("__get_year_from_timestamp")
    date = str(time.strftime("%Y-%m-%d", time.localtime(Config.BACKTEST_BUY_SIGNAL_TIMESTAMP)))
    date = datetime.datetime.strptime(str(date), "%Y-%m-%d")
    return date.year


def __get_unix_timestamp(date):
    print("__get_unix_timestamp")
    date_time = datetime.datetime.strptime(date,
                                           "%Y-%m-%d, %H:%M:%S")
    unix_time = datetime.datetime.timestamp(date_time)
    return int(unix_time)


def delete_backtest_table_file():
    file_name = BrainConfig.BACKTEST_EXECUTION_LIST_FILE_PATH
    if os.path.isfile(file_name):
        os.remove(file_name)
