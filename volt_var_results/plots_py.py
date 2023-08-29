from pprint import pprint as pp
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter
import pandas as pd
import ast
import os
import re
import numpy as np
import random
from datetime import datetime, timedelta


# Test_case_files_2 seems to be working just fine ...
class volt_var_results:

    def __init__(self):

        self.main_dir = os.getcwd()
        self.csv_files = self.main_dir+'/test_case_files_2/'
        self.va_c = []
        self.va_b = []
        self.timestamp = []
        self.pnv_b = []           # This is measurements for node 645, both phases.
        self.pnv_c = []
        # self.n645_va_mags = []
        # self.n645_pnv_mags = []
    
    def get_timestamp (self):
        df = pd.read_csv(self.csv_files+self.file, usecols=['Timestamp'])
        for index, row in df.iterrows():
            self.timestamp.append(row[0])

    def get_cols(self):

        self.df = pd.read_csv(self.csv_files+self.file)
        self.cols = [col for col in self.df.columns if not 'EnergyConsumer' in col and not 'Timestamp' in col]

    def read_files_by_col (self):
        for col in self.cols:
            for key, value in self.df[col].items():
                try:
                    self.parsed_values = ast.literal_eval(value)
                    # self.testing(col = col)
                    self.get_pnv_groups()
                    self.get_va_groups()
                except SyntaxError:
                    pass
    
    def testing(self, col):
        if (self.parsed_values['MeasType'] == 'PNV') and (self.parsed_values['Bus'] == 'n645'):
            print(self.parsed_values['Bus'],'\t',self.parsed_values['Conducting Equipment Name'],'\t', col,'\t',
                   self.parsed_values['magnitude'],'\t', self.parsed_values['Phases'])
            # self.pnv.append(self.parsed_values)

    def get_pnv_groups(self):
        
        if self.parsed_values['Bus'] == 'n645' and self.parsed_values['MeasType'] == 'PNV':
            if self.parsed_values['Phases'] == 'C':
                self.pnv_c.append(self.parsed_values['magnitude'])
            else:
                self.pnv_b.append(self.parsed_values['magnitude'])

    def get_va_groups(self):
        if self.parsed_values['Bus'] == 'n645' and self.parsed_values['MeasType'] == 'VA':
            if self.parsed_values['Conducting Equipment Name'] != 'ol645-646':
                if self.parsed_values['Conducting Equipment Name'] == 'ol_645_b':
                    self.va_b.append(self.parsed_values['magnitude'])
                if self.parsed_values['Conducting Equipment Name'] == 'ol_645_c':
                    self.va_c.append(self.parsed_values['magnitude'])
                # self.n645_va_mags.append({self.parsed_values['Conducting Equipment Name']:
                #                           self.parsed_values['magnitude']})

    def get_va_buses(self):
        pass
    
    def initialize_logs(self):
        meas_files = [i for i in os.listdir(self.csv_files)]
        self.meas_files = sorted(meas_files, key=lambda x: x.split('_')[6])

        for self.file in self.meas_files:
            self.get_cols()
            self.read_files_by_col()
            self.get_timestamp()

class plotting_data:

    def __init__(self):
        
        self.vv = volt_var_results()
        self.vv.initialize_logs()
        self.pnv_b = self.vv.pnv_b
        self.pnv_c = self.vv.pnv_c
        self.phase_va_b = self.vv.va_b
        self.phase_va_c = self.vv.va_c
        self.ts = self.vv.timestamp

        self.combined_list = []

    def scale_data (self, scaling_factor, list_of_values):
        return [round(i/scaling_factor,5) for i in list_of_values]

    def plot_data(self):
        fig, ax1 = plt.subplots(1,figsize=(12,9))

        x = [i.split(' ')[1] for i in self.ts]
        y1 = self.scale_data(scaling_factor=1e3, list_of_values=self.pnv_c)
        y2 = self.scale_data(scaling_factor=1e3, list_of_values=self.phase_va_c)
        color_ax1 = 'tab:red'
        color_ax2 = 'tab:blue'
        
        ax1.plot(x,y1, color=color_ax1, label = 'Voltage (kV)')
        ax1.set_xlabel('Time', fontsize=16)
        ax1.set_ylabel('Voltage (kV)', fontsize=16)
        ax1.tick_params(axis='y', labelcolor=color_ax1)
        ax1.tick_params(axis='x', labelrotation = 45)
        
        
        # Set a secondary y-axis (sharing the x-axis):
        ax2 = ax1.twinx()
        ax2.plot(x, y2, label = 'Demand (kVA)')
        ax2.set_ylabel('Demand (kVA)', fontsize=16)
        ax2.tick_params(axis='y', labelcolor=color_ax2)
        ax2.tick_params(axis='x', labelrotation = 45)
        
        # Axis parameters:
        ax1.xaxis.set_major_locator(ticker.LinearLocator(30))
        ax1.set_ylim(2.360,2.385)
        ax1.set_xlim(min(x), max(x))

        ax2.xaxis.set_major_locator(ticker.LinearLocator(30))
        ax2.set_ylim(0,1200)

        # Horizontal Line:
        l1 = ax1.axhline(y=2.376, color='tab:gray', ls='--')
        l1.set_alpha(0.5)
        l1.set_label("Voltage Tolerance = 1%")

        # Legends and Labels:
        handles_ax1, labels_ax1 = ax1.get_legend_handles_labels()
        handles_ax2, labels_ax2 = ax2.get_legend_handles_labels()
        handles = handles_ax1 + handles_ax2
        labels = labels_ax1 + labels_ax2
        ax1.legend(handles, labels, loc='upper right')

        # plt.axhline(y= 2.376, color = 'tab:gray', linestyle = '--', alpha = 0.5, label = "Voltage Tolerance = 1%")

        fig.suptitle("Voltage Support Grid Service\nVolt-VAr\nTest Case", size = 16, fontweight='bold')
        fig.tight_layout()

        plt.grid()
        plt.show()

plots = plotting_data()
plots.plot_data()