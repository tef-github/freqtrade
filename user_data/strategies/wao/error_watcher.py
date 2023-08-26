import subprocess
import threading

import watchdog.events
import watchdog.observers
import time

from wao.brain_config import BrainConfig

from execution.config import Config
from execution.romeo import Romeo
from execution.system_core import RomeoExitPriceType
from commons.notifier import Notifier


def is_freqtrade_error(error_line):
    lower_string = error_line.lower()
    return "freqtrade" in lower_string and ("warning" in lower_string or "error" in lower_string)


def is_timed_out_error(error_line):
    lower_string = error_line.lower()
    return "connection timed out" in lower_string or "read timed out" in lower_string or "internal error; unable to process your request" in lower_string


def stop_bot(error_line):
    stop_bot_command = "python3 " + BrainConfig.FREQTRADE_PATH + "/wao/stop_bot.py " + str(
        BrainConfig.MODE) + " " + Config.BRAIN + " " + Config.COIN + " " + error_line.split("\n")[0].replace("_", "") \
                           .replace(": ", ":").replace(" ", "#").replace("(", "").replace(")", "")
    result_log = subprocess.Popen([stop_bot_command],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, shell=True, executable='/bin/bash')

    out, err = result_log.communicate()
    out_put = out.decode('latin-1')


def smooth_system_restart(error_line, notifier):
    romeo = BrainConfig.ROMEO_POOL.get(Config.COIN)
    is_system_alive = romeo is not None
    error_line = "[REPORT TO TRELLO] " + error_line
    error_line += ("[SENDING SS]" if is_system_alive else " [POOL EMPTY. NO SYSTEM INSTANCE FOUND]")
    print("smooth_system_restart: is_system_alive="+str(is_system_alive))
    if is_system_alive:
        romeo.is_error = True
        romeo.perform_sell_signal(RomeoExitPriceType.SS)
        romeo.send_error_report(error_line)  # send_to_trello_and_telegram
    else:
        send_to_trello_and_telegram(title=error_line, description=error_line, notifier=notifier)


def string_to_list(string):
    return list(string.split("\n"))


def get_tail_cmd_result(file_name):
    tail_command = "tail -n 100 " + file_name
    result = subprocess.Popen([tail_command],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, shell=True, executable='/bin/bash')
    out, err = result.communicate()
    out_put_string = out.decode('latin-1')
    return string_to_list(out_put_string)


def check_error_condition(file_name, notifier):
    error_line = get_error_line(file_name)

    if error_line is not None and not is_freqtrade_error(error_line) and not is_timed_out_error(error_line):
        is_error_watcher_throttle_hit = time.time() - BrainConfig.PREVIOUS_ERROR_TIMESTAMP_SECONDS > 3

        if BrainConfig.IS_SMOOTH_ERROR_HANDLING_ENABLED and is_error_watcher_throttle_hit:
            smooth_system_restart(error_line, notifier)
        else:
            stop_bot(error_line)
            send_to_trello(title="[STOPBOT] "+error_line, description="is_error_watcher_throttle_hit=" + str(is_error_watcher_throttle_hit) + " " + error_line)
        BrainConfig.PREVIOUS_ERROR_TIMESTAMP_SECONDS = time.time()


def populate_last_error_lines(line_lower):
    if len(BrainConfig.LAST_ERROR_LINES) <= 3:
        BrainConfig.LAST_ERROR_LINES.append(line_lower)
    else:
        BrainConfig.LAST_ERROR_LINES.pop()
        BrainConfig.LAST_ERROR_LINES.insert(0, line_lower)


def get_error_line(file_name):
    list_of_lines = get_tail_cmd_result(file_name)
    if len(list_of_lines) > 0:
        for line in list_of_lines:
            line_str = str(line)
            line_lower = line_str.lower()
            if ("error" in line_lower or "exception" in line_lower) and (
                    line_lower not in BrainConfig.LAST_ERROR_LINES):
                populate_last_error_lines(line_lower)
                return line_str
    return None


def send_to_trello_and_telegram(title, description, notifier):
    notifier.create_trello_bug_ticket(title, description)
    notifier.post_request(description, is_from_error_report=True)


def send_to_trello(title, description):
    notifier = Notifier(BrainConfig.MODE)
    notifier.create_trello_bug_ticket(title, description)


class Error_Watcher(watchdog.events.PatternMatchingEventHandler):

    def __init__(self, notifier):
        watchdog.events.PatternMatchingEventHandler.__init__(self, ignore_directories=False, case_sensitive=False)
        self.notifier = notifier
        
    def on_created(self, event):
        self.__check_error_condition(event)

    def on_modified(self, event):
        self.__check_error_condition(event)
        
    def __check_error_condition(self, event):
        file_name = str(event.src_path)
        threading.Thread(target=check_error_condition, args=(file_name, self.notifier)).start()
