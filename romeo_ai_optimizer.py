import pandas as pd
from random import randrange
import os
import time


def backtest(DUP,MAX_COUNT_DUP):
    return randrange(1,100) # cumulative profit out of 100


class Romeo_ai_optimizer:
    def __init__(self):
        self.DUP_FLOOR = 0.1
        self.DUP_CEILING = 1
        self.MAX_COUNT_DUP_FLOOR = 1
        self.MAX_COUNT_DUP_CEILING = 4
        self.DUP_STEP_FORWARD = 0.1
        self.MAX_COUNT_DUP_STEP_FORWARD = 1
        self.combinations = []
        self.best_combination = [0,0,0]
        self.indentation = "    "   
        self.brain_config_dir = "wao/brain_config.py"
        self.strategy_configuration = [{"config":"config2.json","strategy":"Strategy002"}]
        self.cumulative_profit_path = '../execution/_cumulative_profit.txt'

    def get_month_string(self,month):
        print("get_month_string:month=",month)
        if len(str(month))==1:
            return "0"+str(month)
        return str(month)

    def float_range(self,min,max,step):
        float_range_list = []
        i=min
        while(i<=max):
            float_range_list.append(i)
            i+=step
        return float_range_list
    
    def change_parameters_in_config(self,D_UP,D_UP_MAX):
        with open(self.brain_config_dir,'rt') as config:
            code = config.readlines()
            for i in range(len(code)):
                line = code[i]
                if line.startswith(self.indentation+"BACKTEST_DUP"):
                    line = line.split()
                    line[2] = str(D_UP)
                    line = self.indentation+line[0]+' '+line[1]+' '+str(line[2])+"\n"
                    code[i] = line

                if line.startswith(self.indentation+"BACKTEST_MAX_COUNT_DUP"):
                    line = line.split()
                    line[2] = str(D_UP_MAX)
                    line = self.indentation+line[0]+' '+line[1]+' '+str(line[2])+"\n"
                    code[i] = line
            with open(self.brain_config_dir,'wt') as config:
                config.writelines(code)
        print("Romeo_ai_optimizer: change_parameters_in_config: successfully written DUP and MAX_COUNT_DUP to brain_config.py")

    def change_month_year_for_data_cleaner(self,month,year):
        with open(self.brain_config_dir,'rt') as config:
            code = config.readlines()
            for i in range(len(code)):
                line = code[i]
                if line.startswith(self.indentation+"BACKTEST_DATA_CLEANER_YEAR"):
                    line = line.split()
                    line[2] = year
                    line = self.indentation+line[0]+' '+line[1]+' '+str(line[2])+"\n"
                    code[i] = line

                if line.startswith(self.indentation+"BACKTEST_DATA_CLEANER_MONTH_INDEX"):
                    line = line.split()
                    line[2] = int(month)
                    line = self.indentation+line[0]+' '+line[1]+' '+str(line[2])+"\n"
                    code[i] = line
            with open(self.brain_config_dir,'wt') as config:
                config.writelines(code)
    
    def initiate_backtest(self,coin="BTC",month=1,year=2020):
        print("Romeo-AI-Optimizer: Started running backtests")
        # print("Romeo-AI-Optimizer: Strategy=",strategy)
        print("Romeo-AI-Optimizer: Coin=",coin)
        print("Romeo-AI-Optimizer: month=",1)
        # change the backtest month and year in brain_config.py
        self.change_month_year_for_data_cleaner(int(month)-1,year)

        for strategy in self.strategy_configuration:
            for dup in self.float_range(self.DUP_FLOOR,self.DUP_CEILING,self.DUP_STEP_FORWARD):
                for dup_max_counter in self.float_range(self.MAX_COUNT_DUP_FLOOR,self.MAX_COUNT_DUP_CEILING,self.MAX_COUNT_DUP_STEP_FORWARD):
                    # Change the parameters in brain_config2022-04-12 16:30:48,856 - freqtrade - ERROR - Incorrect syntax for 2022-04-12 16:30:48,856 - freqtrade - ERROR - Incorrect syntax for timerange "2020101-2020201"timerange "2020101-2020201"
                    self.change_parameters_in_config(dup,dup_max_counter)
                    # download the data
                    # source ./.env/bin/activate;
                    commands = """
                    freqtrade download-data --config """+strategy["config"]+""" -t 5m --timerange """+str(year)+self.get_month_string(int(month))+"""01-"""+str(year)+self.get_month_string(int(month)+1)+"""01;
                    python3 wao/freq_data_cleaner.py user_data/data/binance/BTC_USDT-5m.json;
                    cd ../execution/;
                    python3 month_data_download.py BTC """+self.get_month_string(int(month)-1)+""" """+str(year)+""";
                    cd ../freqtrade;
                    screen -L -Logfile Logfile-BTC-Strategy002-Backtest-12:41:00-April-16-2022.txt freqtrade backtesting -c """+strategy["config"]+""" -s """+strategy["strategy"]+""";
                    """
                    print(commands)
                    os.system(commands)
                    cumulative_profit = self.read_cumulative_profit_from_file()
                    if(self.best_combination[2]<cumulative_profit):
                        self.best_combination[0] = dup
                        self.best_combination[1] = dup_max_counter
                        self.best_combination[2] = cumulative_profit

                    # write the combinations to the list
                    self.combinations.append([dup,dup_max_counter,cumulative_profit])
            break
            print("Best combination: ",self.best_combination)
            self.write_to_csv(self.best_combination,"Best combination for coin: "+coin+" strategy: "+strategy["strategy"]+" month: "+str(month+1)+" year: "+str(year)+".csv")
            # call to writing the test combinations to a csv file
            self.write_to_csv(self.combinations,"Combinations for Coin: "+coin+" strategy: "+strategy["strategy"]+" month: "+str(month+1)+" year: "+str(year)+".csv")

    def write_to_csv(self,array,filename):
        # write to csv using pandas
        df = pd.DataFrame(array)
        df.to_csv(filename,index=False)
    def read_cumulative_profit_from_file(self):
        # Run the backtest system and get the cumulative profit
        with open(self.cumulative_profit_path,'rt') as cumulative_profit:
            # get the cumulative profit from the file
            cumulative_profit = cumulative_profit.read()
            return cumulative_profit


if __name__=="__main__":
    romeo_ai_optimizer_runner = Romeo_ai_optimizer()
    romeo_ai_optimizer_runner.initiate_backtest(month="01",year="2021")
    # print(romeo_ai_optimizer_runner.read_cumulative_profit_from_file())
    



# month values are index values
