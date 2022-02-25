import os

from user_data.strategies.config import Config


def create_dir():
    if not os.path.exists(Config.EXECUTION_COMMUNICATION_FILE_PATH):
        os.makedirs(Config.EXECUTION_COMMUNICATION_FILE_PATH)


def write_execution_file(pair, brain):
    create_dir()
    os.mknod(get_full_file_path_name(pair, brain))


def execution_exists(pair, brain):
    return os.path.exists(get_full_file_path_name(pair, brain))


def write_sell_signal(pair, brain):
    f = open(get_full_file_path_name(pair, brain), "a")
    f.write("sell_signal")
    f.close()


def get_file_name(pair, brain):
    return brain + "_" + pair


def get_full_file_path_name(pair, brain):
    return Config.EXECUTION_COMMUNICATION_FILE_PATH + get_file_name(pair, brain)
