EXECUTION_PATH = '/root/workspace2/execution'  # do not move this to brain_config.py

import requests
import sys
import time
from wao._429_file_util import delete_429_file, write_to_429_file
from wao.brain_config import BrainConfig

sys.path.append(EXECUTION_PATH)
from config import Config

TELEGRAM_RESPONSE_200 = "<Response [200]>"


def send_start_deliminator_message(brain, coin, month, year, dup, max_counter_dup):
    print("notifier: send_start_deliminator_message: ")
    print("month-------------------",month)
    print("type of month-----------",type(month))
    print("year-------------------",year)
    print("type of year-----------",type(year))
    print("dup-------------------",dup)
    print("type of dup-----------",type(dup))
    print("dup-------------------",max_counter_dup)
    print("type of max_counter_dup-----------",type(max_counter_dup))
    text = "========" + str(brain) + " DUP = " + str(dup) + " MAX_COUNTER_DUP = " + str(max_counter_dup) + " " + str(
        coin) + " " + str(month) + " " + str(year) + "=======>"

    post_request(text)


def post_request(text, is_from_429_watcher=False):
    print("post_request: " + text)
    telegram_bot_api_token = Config.NOTIFIER_TELEGRAM_BOT_API_TOKEN_429 if is_from_429_watcher else Config.NOTIFIER_TELEGRAM_BOT_API_TOKEN_BACKTEST
    result = requests.post('https://api.telegram.org/bot' + telegram_bot_api_token +
                           '/sendMessage?chat_id=' + Config.NOTIFIER_TELEGRAM_CHANNEL_ID_BACKTEST +
                           '&text=' + text + '&parse_mode=Markdown')

    print(str(result))

    if BrainConfig.IS_429_FIX_ENABLED:
        if str(result) != TELEGRAM_RESPONSE_200:
            delete_429_file(text)
            write_to_429_file(text)
        elif str(result) == TELEGRAM_RESPONSE_200 and is_from_429_watcher:
            delete_429_file(text)
