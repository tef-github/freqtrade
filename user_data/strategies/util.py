import subprocess

IS_BACKTEST = False

EXECUTION_PATH = "/root/workspace2/execution/"

def launcher(mode, coin, brain):
    subprocess.call("python3 "+EXECUTION_PATH+"launcher.py " + mode + " " + coin + " " + brain, shell=True)

def back_tester(date_time, coin, brain):
    date = str(date_time)
    date = date.replace(" ", "#")
    subprocess.call("python3 "+ EXECUTION_PATH + "back_tester.py " + date + " " + coin + " " + brain + " 0.45 3", shell=True)
