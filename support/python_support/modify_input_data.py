import os
import random
import pandas as pd
from pprint import pprint as pp


# HDI --> Historical Data Input

class add_remove_modify_HDI:

    def __init__(self):
        
        self.main_dir = os.getcwd()
        self.input_files_path = "../../DERSHistoricalDataInput/"
        self.input_files_destination = "../../ders_testing/"
    
    def add_rows(self, df, time, watts, vars, loc):
        new_row = pd.DataFrame([[time, watts, vars, loc]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        return df

    def modify_rows(self):
        pass

    def remove_rows(self, df):
        return df.head(0)
    
    def remove_columns(self, df):
        return df.drop(df.columns[3], axis=1)

    def read_files(self, file):
        df = pd.read_csv(self.input_files_path+file)
        self.constant_value = df.iloc[0][df.columns[-1]] # DER location never changes
        return df
    
    def write_files (self, df, files_name):
        df.to_csv(self.input_files_destination+files_name, index=False)



    def main_loop(self):
        for file in os.listdir(self.input_files_path):
            if file.startswith("ders"):
                df = self.read_files(file)
                df = self.remove_rows(df)
                # df = self.remove_columns(df)
                df = self.add_rows(df=df, time=1570041117 ,watts=random.randint(0,4500),
                                   vars=0, loc=self.constant_value)
                
                df = self.add_rows(df=df, time=1570041124 ,watts=random.randint(0,4500),
                                   vars=0, loc=self.constant_value)
                
                df = self.add_rows(df=df, time=1570041130 ,watts=random.randint(0,4500),
                                   vars=0, loc=self.constant_value)
                self.write_files(df=df, files_name=file)
                

class add_remove_modify_rwhders:

    def __init__(self):
        
        self.hist_data = add_remove_modify_HDI()
        self.dir = self.hist_data.main_dir
        self.input_files = "../../RWHDERS_Inputs"
        self.destination = self.input_files
    
    def add_rows(self, watts, file_name):
        print(f'P,{watts}', file=file_name)
    
    def main_loop (self):
        for file in os.listdir(self.input_files):
            data_to_write = open(f'{self.input_files}/{file}', 'w')
            self.add_rows(watts=random.randint(0,4500), file_name=data_to_write)
            data_to_write.close()

# rwh = add_remove_modify_HDI()
# rwh.main_loop()

class combine_ders_files:

    def __init__(self):
        self.main_dir = '../../DERSHistoricalDataInput'
        self.dfs = {}
    
    def read_files (self):
        for file in os.listdir(self.main_dir):
            if file.startswith('ders'):
                df = pd.read_csv(self.main_dir+'/'+file)
                time = df.columns[0]
                # df = df.drop('Time', axis=1)
                self.dfs[time].append(df.iloc[:,1:])
        combined_dfs = pd.concat(self.dfs.values(), axis=1, keys=self.dfs.keys())
        pp(combined_dfs)
    
    def combine_dfs(self):
        dfs = pd.concat(self.dfs, ignore_index=True)
        print(dfs)


ders = combine_ders_files()
ders.read_files()