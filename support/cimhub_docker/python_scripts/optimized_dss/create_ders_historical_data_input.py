import os
import numpy as np
import pandas as pd
from pprint import pprint as pp
from pathlib import Path as path

class get_ders_historical_data():

    def __init__(self):
        self.current_dir = os.getcwd()
        self.der_loc_file = './dss/psu_feeder_coordinates.csv'
        self.nodes = ["680","633","632","692","675","671","684","645","652", "611"]
        self.me_dir = '/home/deras/Desktop/midrar_work_github/doe-egot-me/'
        self.watt_files = '/home/deras/Desktop/midrar_work_github/populated_13_node_feeder_whs/glm/glm_output/'
    
    def get_int(self,x):                     #Called in sort_list func. Not in main
        return int(x.split('_')[-1])

    def sort_list(self, der_s_busses):        #Called in get_der_loc func. Not in main
        return sorted(der_s_busses, key=self.get_int)
    
    def get_der_loc (self):
        der_s_busses = []
        df = pd.read_csv(self.der_loc_file, names = ['bus','x','y'])
        
        filtered_df = df[df['bus'].str.startswith("trip_node")]
        for node in self.nodes:
            for index, row in filtered_df.iterrows():
                if node in row.to_string():
                    der_s_busses.append(row['bus'])
        self.der_s_busses = list(set(sorted(der_s_busses)))
        
    def read_watts(self):

        self.watts_values = []
        sorted_watts_profiles = sorted([file_names for file_names in os.listdir(self.watt_files)], 
                                       key=lambda x: int((x.split('meter_')[1]).split(".")[0]))
        
        for file_index in range(len(self.der_s_busses)):
            
            try:
                df = pd.read_csv(self.watt_files+sorted_watts_profiles[file_index], skiprows=7)
                df = df.drop('# timestamp', axis=1)
                for cols in df.columns:
                    for key, value in df[cols].iteritems():
                        self.watts_values.append(value)
            except IndexError:
                break

    def concat_bus_watts(self):
        j = 0
        k = 1439
        self.ders = {}
        
        for i in range(len(self.der_s_busses)):
            self.ders[f'DER{i}_mag'] = self.watts_values[j:k]
            self.ders[f'DER{i}_loc'] = self.der_s_busses[i]
            j = k
            k += 1439
        
        
    def uppercase_to_lowercase(self):
        self.df = pd.DataFrame.from_dict(self.ders)
        self.df = self.df.applymap(lambda x: x.lower() if type(x) == str else x)
    
    def float_to_int(self):
        float_cols = [col for col in self.df.columns if self.df[col].dtype =='float64']
        self.df[float_cols] = self.df[float_cols].astype(int)
        
    
    def create_time_col(self):
        
        starting_time = 1672531200
        
        timestamp = pd.date_range(start=pd.to_datetime(starting_time, unit='s'),
                                  freq='1min', periods=len(self.df['DER0_mag']))
        
        time_df = pd.DataFrame({'Time':timestamp})

        time_df = time_df['Time'].astype(int) // 10**9

        self.df = pd.concat([time_df, self.df], axis=1)

    
    def wr_csv(self):
        print(self.df)
        self.df.to_csv(f'{self.me_dir}DERSHistoricalDataInput/psu_feeder_ders_data.csv', index=False)

if __name__ == '__main__':
    ders = get_ders_historical_data()
    ders.get_der_loc()
    # ders.append_busses_to_df()
    ders.read_watts()
    ders.concat_bus_watts()
    ders.uppercase_to_lowercase()
    ders.float_to_int()
    ders.create_time_col()
    ders.wr_csv()