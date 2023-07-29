import os
import ast
import pandas as pd
from pprint import pprint as pp
import xml.etree.ElementTree as et

class filter_measurements ():

    def __init__(self):
        self.path = "../Logged_Grid_State_Data/"
    
    def read_files (self, file):
        """
        If file does not start with 'Meas', then this function will return None
        """
        if file.startswith('Meas'):
            df = pd.read_csv(self.path+file)
            return df
    
    def drop_timestamp(self, df):
        """
        Replace the following return statement with a 'pass' statement if you need the timestamp column
        """
        return df.drop('Timestamp', axis=1)
    
    def parse_files (self, row):
        """
        Makes rows in each file looks like a dictionary. It's AWESOME!
        """
        return ast.literal_eval(row)

    def get_VAs(self, parsed_file, meas_type):
        """
        You can filter the measurements anyway you want. I find it more useful to filter them based on their type.
        In this function, Apparent power measurements are returned.
        """
        if parsed_file['MeasType'] == meas_type:
            pass # Do what you want
            
    def get_PNVs (self, parsed_file, meas_type):
        """
        In this function, phase voltage measurements are returned.
        """
        if parsed_file['MeasType'] == meas_type:
            pass # Do what you want
    
    def main_loop(self):
        for files in os.listdir(self.path): # loop through directory and get files
            df = self.read_files(files)
            if df is not None:
                df = self.drop_timestamp(df)
                for col in df.columns:
                    for index, row in df[col].items():
                        parsed_rows = self.parse_files(row)
                        self.get_VAs(parsed_file=parsed_rows, meas_type='VA')
                        self.get_PNVs(parsed_file=parsed_rows, meas_type='PNV')
                        

parsing = filter_measurements()
parsing.main_loop()