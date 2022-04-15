class BrainConfig:

    BACKTEST_DUP = 0.1
    BACKTEST_MAX_COUNT_DUP = 1
    BACKTEST_DOWNLOADED_JSON_DATA_FILE_PATH = ""
    BACKTEST_COIN = 'BTC'
    BACKTEST_MONTH_LIST = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    BACKTEST_DATA_CLEANER_YEAR = 2021
    BACKTEST_DATA_CLEANER_MONTH_INDEX = 0
    IS_BACKTEST = True
    WORKSPACE_PATH = "workspace2" if IS_BACKTEST else "workspace"
    _429_DIRECTORY = "/root/" + WORKSPACE_PATH + "/freqtrade/_429_directory/"
    IS_PARALLEL_EXECUTION = True
    IS_429_FIX_ENABLED = False