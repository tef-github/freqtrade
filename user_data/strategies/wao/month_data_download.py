import csv
import os
from binance.client import Client
import sys
from execution.config import Config
from execution.keys import Keys


def download_data():
    print("download_data:...")
    client = Client(Keys.BINANCE_API_KEY, Keys.BINANCE_API_SECRET)

    current_month_index = Config.BACKTEST_MONTH_INDEX
    next_month_index = Config.BACKTEST_MONTH_INDEX + 1
    current_year_index = Config.BACKTEST_YEAR
    next_year_index = Config.BACKTEST_YEAR
    if current_month_index == 11:
        next_month_index = 0
        next_year_index += 1

    candlesticks = client.get_historical_klines(Config.COIN + Config.get_stable_coin(Config.COIN), Config.BACKTEST_TIME_FRAME,
                                                str(current_month_index + 1) + " 1, " + str(
                                                    current_year_index),
                                                str(next_month_index + 1) + " 1, " + str(
                                                    next_year_index))
    write_to_csv(candlesticks)


def create_data_directory():
    print("create_data_directory:..." + Config.BACKTEST_DOWNLOAD_DATA_DIRECTORY + "...")
    if not os.path.exists(Config.BACKTEST_DOWNLOAD_DATA_DIRECTORY):
        os.mkdir(Config.BACKTEST_DOWNLOAD_DATA_DIRECTORY)


def write_to_csv(candlesticks):
    print("write_to_csv:...")
    create_data_directory()
    csvfile = open(
        Config.BACKTEST_DOWNLOAD_DATA_DIRECTORY + "/" + Config.COIN + "_" + Config.BACKTEST_TIMEFRAME_READABLE + "_" +
        Config.MONTH_LIST[Config.BACKTEST_MONTH_INDEX] + '_' + str(Config.BACKTEST_YEAR) + Config.CSV_FORMAT, 'w',
        newline='')
    candlestick_writer = csv.writer(csvfile, delimiter=',')
    for candlestick in candlesticks:
        candlestick[0] = candlestick[0] / 1000
        candlestick_writer.writerow((int(candlestick[0]), candlestick[4]))
    csvfile.close()


if len(sys.argv) < 4:
    exit("""Incorrect number of arguments. 
    python3 month_data_download.py [coin] [month_index] [year]
    """)
else:
    Config.COIN = sys.argv[1]
    Config.BACKTEST_MONTH_INDEX = int(sys.argv[2]) if int(sys.argv[2]) < 12 else 0
    Config.BACKTEST_YEAR = int(sys.argv[3])
    download_data()
    print(
        "month_data_download.py: " + Config.BACKTEST_DOWNLOAD_DATA_DIRECTORY + Config.COIN + "_" + Config.BACKTEST_TIMEFRAME_READABLE + "_" +
        Config.MONTH_LIST[Config.BACKTEST_MONTH_INDEX] + "_" + str(
            Config.BACKTEST_YEAR) + ".csv" + " has been downloaded.")
