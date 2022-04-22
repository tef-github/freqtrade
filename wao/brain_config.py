class BrainConfig:

    BACKTEST_DUP = 0.45
    BACKTEST_MAX_COUNT_DUP = 2
    BACKTEST_DOWNLOADED_JSON_DATA_FILE_PATH = ""
    BACKTEST_COIN = 'ADA'
    BACKTEST_MONTH_LIST = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    BACKTEST_DATA_CLEANER_YEAR = 2021
    BACKTEST_DATA_CLEANER_MONTH_INDEX = 0
    IS_BACKTEST = True
    CHOP_TESTER_WORKSPACE = "workspace2"
    WORKSPACE_PATH = "workspace2" if IS_BACKTEST else "workspace"
    ROOT_DIRECTORY = "/root/"
    EXECUTION_PATH = ROOT_DIRECTORY + "workspace/execution"
    _429_DIRECTORY = ROOT_DIRECTORY + WORKSPACE_PATH + "/freqtrade/_429_directory/"
    IS_PARALLEL_EXECUTION = True
    BACKTEST_THROTTLE_SECOND = 0.01
    MODE = "test" # test or prod
    CUMULATIVE_PROFIT_FILE_PATH = ROOT_DIRECTORY + WORKSPACE_PATH + "/execution/_cumulative_profit.txt"
