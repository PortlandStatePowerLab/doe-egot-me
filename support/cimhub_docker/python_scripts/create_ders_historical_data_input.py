import os
import numpy as np
import pandas as pd
from pprint import pprint as pp
from pathlib import Path as path

class get_ders_historical_data():

    def __init__(self):
        self.current_dir = os.getcwd()
        self.der_loc_file = './dss_batteries/psu_feeder_coordinates.csv'
        self.me_dir = '/home/deras/Desktop/midrar_work_github/doe-egot-me/'
        self.nodes = ["680","633","632","692","675","671","684","645","652", "611"]
        self.watt_files = '/home/deras/Desktop/midrar_work_github/water-draw-generator/populated_13_node_feeder_whs/glm/glm_output/'
        self.house_files = '/home/deras/Desktop/Midrar_work/thesis_work/feeder_model/basecase/final_files/daily_data/'

    
    def get_int(self,x):                     #Called in sort_list func. Not in main
        return int(x.split('_')[-1])

    def sort_list(self, der_s_busses):        #Called in get_der_loc func. Not in main
        return sorted(der_s_busses, key=self.get_int)
    
    def get_der_loc (self):
        der_s_busses = []
        df = pd.read_csv(self.der_loc_file, names = ['bus','x','y'])
        filtered_df = df[df['bus'].str.startswith("tlx")]
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

    # def read_house_values (self):
    #     self.house_values = []
    #     sorted_house_profiles = sorted([file_names for file_names in os.listdir(self.house_files)], 
    #                                    key=lambda x: int((x.split('house_')[1]).split(".")[0]))
    #     sorted_house_profiles = sorted_house_profiles[:960]
    #     for file_index in range(len(self.der_s_busses)):
        
    #         try:
    #             # print(file_index)
    #             df = pd.read_csv(self.house_files+sorted_house_profiles[file_index])
    #             df = df.drop('timestamp', axis=1)
    #             for cols in df.columns:
    #                 for key, value in df[cols].iteritems():
    #                     self.house_values.append(value)
    #         except IndexError:
    #             break
    #     print('houses --> ',len(self.house_values))
    #     print('watts --> ',len(self.watts_values))

    def concat_bus_watts(self):
        j = 0
        k = 1439
        self.ders = {}
        
        for i in range(len(self.der_s_busses)):
            self.ders[f'DER{i}_real'] = self.watts_values[j:k]
            # self.ders[f'house{i}_mag'] = self.house_values[j:k]
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
        
        # timestamp = pd.date_range(start=pd.to_datetime(starting_time, unit='s'),
        #                           freq='1min', periods=len(self.df['DER0_mag']))
        timestamp = pd.date_range(start=pd.to_datetime(starting_time, unit='s'),
                                  freq='1min', periods=len(self.df['DER0_real']))
        
        time_df = pd.DataFrame({'Time':timestamp})

        time_df = time_df['Time'].astype(int) // 10**9

        self.df = pd.concat([time_df, self.df], axis=1)

    def wr_csv(self):
        self.df = self.df.head(10)
        self.df.to_csv(f'{self.me_dir}DERSHistoricalDataInput/source_file/psu_feeder_ders_data.csv', index=False)
        
    

    def expand_ders(self):
        counter = 0
        df = pd.read_csv(f'{self.me_dir}DERSHistoricalDataInput/source_file/psu_feeder_ders_data.csv')
        for i in range(1, len(df.columns), 2):
            new_df = df.iloc[:, [0,i,i+1]]
            new_df.to_csv(f'{self.me_dir}DERSHistoricalDataInput/ders_{counter}.csv', index=False)
            counter += 1
        
    
    def add_house_profiles (self):
        counter = 0
        sorted_house_profiles = sorted([file_names for file_names in os.listdir(self.house_files)], 
                                    key=lambda x: int((x.split('house_')[1]).split(".")[0]))
        sorted_house_profiles = sorted_house_profiles[:960]

        sorted_wd_profiles = sorted([file_names for file_names in os.listdir(f"{self.me_dir}ders_testing/") if file_names.startswith("ders")], 
                                    key=lambda x: int((x.split('ders_')[1]).split(".")[0]))

        for i in range(960):
            houses = pd.read_csv(self.house_files+sorted_house_profiles[i])
            houses = houses.iloc[:,1] # Read watts column
            ders = pd.read_csv(f"{self.me_dir}DERSHistoricalDataInput/{sorted_wd_profiles[i]}")
            ders[f"HOUSE{i}_mag"] = houses.astype(int)
            
            ders = ders.fillna(0)

            ders = self.add_vars(ders, counter)

            ders = self.rearrange_columns(ders)

            self.wr_house_profiles(ders, counter)


            counter += 1
        

    def rearrange_columns (self, df):
        df = df.iloc[:,[0,1,4,3,2]] # The new order is Time, der_mag, house_mag, der_loc
        return df
        
    def wr_house_profiles (self, ders, counter):
        ders.to_csv(f"{self.me_dir}ders_testing/ders_{counter}.csv", index= False)
    
    def add_vars (self, df, counter):
        df[f'DER{counter}_imag'] = 0
        return df



if __name__ == '__main__':
    ders = get_ders_historical_data()
    ders.get_der_loc()
    ders.read_watts()
    ders.concat_bus_watts()
    ders.uppercase_to_lowercase()
    ders.float_to_int()
    ders.create_time_col()
    ders.wr_csv()
    ders.expand_ders()
    ders.add_house_profiles()
