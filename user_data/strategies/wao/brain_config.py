class BrainConfig:
    BRAIN = ""  # set from strategy files
    IS_SCHEDULE_ORDER = True
    IS_LIMIT_STOP_ORDER_ENABLED = True
    BACKTEST_DOWNLOADED_JSON_DATA_FILE_PATH = ""
    BACKTEST_MONTH_LIST = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    BACKTEST_DATA_CLEANER_YEAR = 2021
    BACKTEST_DATA_CLEANER_MONTH_INDEX = 4
    IS_BACKTEST = False
    IS_ERROR_WATCHER_ENABLED = True
    SYSTEM_POOL = {}  # romeo_pool: key=coin, value=romeo_instance
    WORKSPACE_BACKTEST = "/workspace2"
    WORKSPACE_NORMAL = "/workspace"
    WORKSPACE = WORKSPACE_BACKTEST if IS_BACKTEST else WORKSPACE_NORMAL
    ROOT = "/home/ubuntu"
    FREQTRADE_PATH = ROOT + WORKSPACE + "/freqtrade"
    _429_DIRECTORY = FREQTRADE_PATH + "/_429_directory/"
    _WAO_LOGS_DIRECTORY = FREQTRADE_PATH + "/_wao_logs/"
    BACKTEST_SIGNAL_LIST_PICKLE_FILE_PATH = FREQTRADE_PATH + "/_backtest_list.pickle"
    BACKTEST_SIGNAL_LIST = []
    BACKTEST_THROTTLE_SECOND = 1
    MODE = "test"  # test or prod
    CUMULATIVE_PROFIT_FILE_PATH = FREQTRADE_PATH + "/_cumulative_profit.txt"
    CUMULATIVE_PROFIT_BINANCE_FILE_PATH = FREQTRADE_PATH + "/_cumulative_profit_binance.txt"
    INITIAL_ACCOUNT_BALANCE_BINANCE_FILE_PATH = FREQTRADE_PATH + "/_initial_account_balance_binance.txt"
    IS_SMOOTH_ERROR_HANDLING_ENABLED = True
    LAST_ERROR_LINES = []
    PREVIOUS_ERROR_TIMESTAMP_SECONDS = 0
