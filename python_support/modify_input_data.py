import os
import pandas as pd
from pprint import pprint as pp

class add_remove_modify_data:

    def __init__(self):
        
        self.main_dir = os.getcwd()
        self.input_files_path = "../DERSHistoricalDataInput/"
        self.input_files_destination = "../ders_testing/"
    
    def add_rows(self, df, time, watts, vars, mag, loc):
        new_row = pd.DataFrame([[time, watts, vars, mag, loc]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        return df

    def modify_rows(self):
        pass

    def remove_rows(self, df):
        return df.head(0)

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
                # df = self.add_rows(df=df, time=1672531206 ,watts=4500, vars=0, mag=0, loc=self.constant_value)
                df = self.add_rows(df=df, time=1672531206 ,watts=4500, vars=0, mag=5000, loc=self.constant_value)
                # df = self.add_rows(df=df, time=1672531209 ,watts=0, vars=0, mag=5000, loc=self.constant_value)
                # df = self.add_rows(df=df, time=1672531206 ,watts=4500, vars=0, mag=0, loc=self.constant_value)
                # df = self.add_rows(df=df, time=1672531220 ,watts=0, vars=0, mag=5000, loc=self.constant_value)
                self.write_files(df=df, files_name=file)
                

ders = add_remove_modify_data()
ders.main_loop()