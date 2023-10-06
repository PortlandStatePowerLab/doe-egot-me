from matplotlib.ticker import FuncFormatter
import matplotlib.ticker as ticker
from matplotlib import rcParams
from pprint import pprint as pp
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import ast
import os

class FilterData:

    def __init__(self):
        
        self.main_dir = os.getcwd()
        self.csv_files = self.main_dir+'/case_files/'
        self.dfs = []
    
    def read_measurements_files(self, new_file):

        self.data_files = pd.read_csv(self.csv_files+new_file)
        self.meas_data = {}
    
    def iterate_over_columns(self):
        for self.col in self.data_files.columns:

            if '_ol_' in self.col:

                for key, item in self.data_files[self.col].items():
                     self.formatted_row = ast.literal_eval(item)
                    
                    # Get main nodes:

                     if self.formatted_row['Bus'].startswith('n'):
                         self.get_voltage_measurements()
                         self.get_volt_ampere_measurements()
            
            elif 'PowerElectronicsConnection' in self.col:

                for key, item in self.data_files[self.col].items():
                    self.formatted_row = ast.literal_eval(item)
                    
                    if self.formatted_row['Bus'].startswith('tlx'):
                        self.get_voltage_measurements()
                        self.get_volt_ampere_measurements()
                        self.get_soc_measurements()
            
            elif 'EnergyConsumer' in self.col:
                for key, item in self.data_files[self.col].items():
                    self.formatted_row = ast.literal_eval(item)
                    
                    if self.formatted_row['Bus'].startswith('tlx'):
                        self.get_voltage_measurements()
                        self.get_volt_ampere_measurements()
            
            elif self.col == 'Timestamp':
                if not 'Timestamp' in self.meas_data:
                    self.meas_data['Timestamp'] = []
                    self.update_timestamp_key()

            elif 'ol671-680' in self.col:
                for key, item in self.data_files[self.col].items():
                     self.formatted_row = ast.literal_eval(item)
                     if self.formatted_row['Bus'] == 'n680':
                        self.get_voltage_measurements()
                        self.get_volt_ampere_measurements()

        self.create_dataframes()
    
    def update_timestamp_key(self):
        for key, value in self.data_files['Timestamp'].items():
            self.meas_data['Timestamp'].append(value)

    
    def update_dict(self, row, att):
        keys = f"{row['Bus']+'_'+row['Conducting Equipment Name']+'_'+row['Phases']+'_'+row['MeasType']}"

        if att == 'angle' and row['MeasType'] != 'SoC':
            if not keys+'_angle' in self.meas_data:
                self.meas_data[keys+'_angle'] = []
            self.meas_data[keys+'_angle'].append(row['angle'])
        
        elif row['MeasType'] == 'SoC':
            if not keys in self.meas_data:
                self.meas_data[keys] = []
            self.meas_data[keys].append(row['value'])

        else:
            if not keys+'_mag' in self.meas_data:
                self.meas_data[keys+'_mag'] = []
            self.meas_data[keys+'_mag'].append(self.formatted_row['magnitude'])
            
    
    def get_voltage_measurements(self):
        if self.formatted_row['MeasType'] == 'PNV' and self.formatted_row['Conducting Equipment Name'].startswith('ol_'):
            self.update_dict(row=self.formatted_row, att='mag')

        elif self.formatted_row['MeasType'] == 'PNV' and self.formatted_row['Conducting Equipment Name'].startswith('ol671'):
            self.update_dict(row=self.formatted_row, att='mag')

        elif self.formatted_row['MeasType'] == 'PNV' and self.formatted_row['Conducting Equipment Name'].startswith('DER_'):
            self.update_dict(row=self.formatted_row, att='mag')
        
        elif self.formatted_row['MeasType'] == 'PNV' and self.formatted_row['Conducting Equipment Name'].startswith('EnergyConsumer_'):
            self.update_dict(row=self.formatted_row, att='mag')
    
    def get_volt_ampere_measurements(self):
        if self.formatted_row['MeasType'] == 'VA' and self.formatted_row['Conducting Equipment Name'].startswith('ol_'):
            self.update_dict(row=self.formatted_row, att='angle')
            self.update_dict(row=self.formatted_row, att='mag')

        elif self.formatted_row['MeasType'] == 'VA' and self.formatted_row['Conducting Equipment Name'].startswith('DER_'):
            self.update_dict(row=self.formatted_row, att='angle')
            self.update_dict(row=self.formatted_row, att='mag')
        
        elif self.formatted_row['MeasType'] == 'VA' and self.formatted_row['Conducting Equipment Name'].startswith('house_'):
            self.update_dict(row=self.formatted_row, att='angle')
            self.update_dict(row=self.formatted_row, att='mag')
    
    def get_soc_measurements(self):
        if self.formatted_row['MeasType'] == 'SoC' and self.formatted_row['Conducting Equipment Name'].startswith('DER_'):
            self.update_dict(row=self.formatted_row,att='SoC')
        

    def create_dataframes (self):
        self.df = pd.DataFrame(self.meas_data)
        self.dfs.append(self.df)
    
    def combine_dataframes(self):
        self.combined_dfs = pd.concat(self.dfs, ignore_index=True)
    
    def sort_files (self):
        x = [file for file in os.listdir(self.csv_files) if file.endswith('csv') and file.startswith('MeasOutputLogs')]
        x = sorted(x, key=lambda x: int(x.split('.csv')[0].split('_')[6]))
        return x
    
    def write_file (self):
        self.combined_dfs.to_csv(f'{self.csv_files}one_file_measurements.csv', index=False)



class PlottingFilteredData:

    def __init__(self):

        self.filter_data = FilterData()
        self.dir = f"{self.filter_data.csv_files}"
        self.dfs = []

    def check_files(self):
        file_status = 'exists'
        for files in os.listdir(self.filter_data.csv_files):
            if files.startswith('one'):
                print(f'The One file,{files} ,exists. Heading to plotting!')
                return file_status
        else:
            return 'File does not exist'

    def read_dataframe(self):
        self.df = pd.read_csv(self.dir+'one_file_measurements.csv')
        
        col_sum = ['n633_ol_633_a_A_VA_mag','n633_ol_633_b_B_VA_mag','n633_ol_633_c_C_VA_mag']
        self.df['result'] = self.df[col_sum].sum(axis=1)
    

    def plotting (self):

        x = pd.to_datetime(self.df['Timestamp']).dt.strftime('%H:%M:%S')
        y = self.df['result']/1e3
        x = x.iloc[8:]
        y = y.iloc[8:]

        fig, ax1 = plt.subplots(1,figsize=(12,9), dpi=100)
        color_ax1 = 'tab:gray'

        ax1.plot(x,y, color=color_ax1, label = 'Demand (kVA)')
        ax1.set_xlabel('Time', fontsize=16)
        ax1.set_ylabel('Demand (kVA)', fontsize=16, color = color_ax1)
        ax1.tick_params(axis='y', labelcolor=color_ax1, length=0)
        ax1.tick_params(axis='x', labelrotation = 45)

        ax1.xaxis.set_major_locator(ticker.LinearLocator(40))
        ax1.set_xlim(min(x), max(x))
        
        handles_ax1, labels_ax1 = ax1.get_legend_handles_labels()
        ax1.legend(handles_ax1, labels_ax1, loc='upper right')

        fig.suptitle("Emergency Grid Service", size = 16, fontweight='bold')
        fig.tight_layout()

        plt.grid()
        plt.show()



pl = PlottingFilteredData()
data = FilterData()

x = pl.check_files()


def plots ():
    pl.read_dataframe()
    pl.plotting()

def create_df ():
    print('create_df')
    files = data.sort_files()

    for f in files:
        data.read_measurements_files(new_file=f)
        data.iterate_over_columns()

    data.combine_dataframes()
    data.write_file()

if x != 'exists':
    create_df()
    plots()

else:
    plots()
