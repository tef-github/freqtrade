from wao.brain_config import BrainConfig
import requests
import sys

sys.path.append(BrainConfig.EXECUTION_PATH)
from config import Config
from _429_file_util import delete_429_file, write_to_429_file

TELEGRAM_RESPONSE_200 = "<Response [200]>"
TELEGRAM_RESPONSE_429 = "<Response [429]>"


def send_start_deliminator_message(brain, coin, month, year):
    print("notifier: send_start_deliminator_message: ")
    text = "========" + str(brain) + " coin=" + str(
        coin) + " " + str(month) + " " + str(year) + "=======>"

    post_request(text)


def post_request(text, is_from_429_watcher=False):
    print("post_request: " + text)
    telegram_bot_api_token = Config.NOTIFIER_TELEGRAM_BOT_API_TOKEN_429 if is_from_429_watcher else Config.NOTIFIER_TELEGRAM_BOT_API_TOKEN_BACKTEST
    result = requests.post('https://api.telegram.org/bot' + telegram_bot_api_token +
                           '/sendMessage?chat_id=' + Config.NOTIFIER_TELEGRAM_CHANNEL_ID_BACKTEST +
                           '&text=' + text.replace("_", "-") + '&parse_mode=Markdown')

    print(str(result))

    if is_from_429_watcher:
        if str(result) == TELEGRAM_RESPONSE_429:
            delete_429_file(text)
            write_to_429_file(text)
        elif str(result) == TELEGRAM_RESPONSE_200:
            delete_429_file(text)
