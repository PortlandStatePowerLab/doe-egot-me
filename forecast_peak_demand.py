import os
import re
import pandas as pd
import os.path as op
from pathlib import Path
import matplotlib.pyplot as plt
from pprint import pprint as pp
from collections import defaultdict

class peak_demand_mitigation:
    '''
    This class forecasts the peak demand times for the DERSHistorical Data inputs. The result is a csv file that
    contains three columns; the first column is for the time of the peak demand, the second column is for the value
    of the peak demand, the third column is for the node where the peak demand is forecasted.
    '''
    def __init__(self):
        
        self.main_dir = op.dirname(os.getcwd())
        self.ders_w_same_buses = {}
    
    def read_demand_files(self, file, data_dir):
        '''
        Read the demand profiles and pick only three hours. The simulation time is a user-preference.
        '''
        self.df = pd.read_csv(data_dir+file)
        self.df['Time'] = pd.to_datetime(self.df['Time'], unit='s')
        self.df = self.df.iloc[360:541,:]                           # Pick only three hours window

    def gather_profiles_with_same_bus(self, file):
        '''
        Group data with the same buses. Since we have 960 load profiles, we create a dictionary with keys defined as
        the bus names, and values as a list of the files for each load connected the bus.
        '''
        bus = self.df.iloc[1,-1].split("_")[1]
        if bus not in self.ders_w_same_buses:
            self.ders_w_same_buses[bus] = []
        
        self.ders_w_same_buses[bus].append(file)
        return self.ders_w_same_buses

    def find_peak_demand(self, peaks_per_node, counter):
        '''
        Iterate over each row in each file, sum up the watts value for each timestamp value, and append it to a 
        dictionary: peaks_per_node.

        The peaks_per_node dict contains timestamps as keys, and the summed up watts as values for that specific
        timestamp. The peaks_per_node dict will be re-initialized with every new group of buses.
        '''
        for index, row in self.df.iterrows():
            self.node = row[3].split("_")[1]
            self.ts = str(row['Time'])
            watts = int(row[1])
            if watts > 0:
                peaks_per_node[self.ts] += watts
                peaks_per_node[f'node_{counter}'] = int(self.node)
        return peaks_per_node

    def get_daily_peaks(self, peaks_per_node, counter):
        '''
        get the highest watt value and its corresponding timestamp. Post the values to a csv file that will be read
        later by the ModelController (MC) to post a grid service for DERMS.
        '''
        
        max_ts = max(peaks_per_node, key=lambda ts:peaks_per_node[ts])
        max_val = peaks_per_node[max_ts]
        bus = peaks_per_node[f'node_{counter}']
        return max_ts, max_val, bus

    def post_peak_demand_time(self, peak_watts_and_times):
        peak_value = float('-inf')
        for row in peak_watts_and_times:
            for key, value in row.items():
                if value[1] > peak_value:
                    peak_value = value[1]
                    max_ts = value[0]
                    bus = key
        posted_time = pd.to_datetime(max_ts)
        posted_time = int(posted_time.timestamp())
        return peak_value, posted_time, bus

# if __name__ == '__main__':
#     pdm = peak_demand_mitigation()
#     data_dir = pdm.main_dir+'/doe-egot-me'+'/DERSHistoricalData_Inputs/'
#     peak_watts_and_times = []
#     counter = 0
#     for file in os.listdir(data_dir):
#         pdm.read_demand_files(file=file, data_dir=data_dir)
#         ders_same_buses = pdm.gather_profiles_with_same_bus(file=file)

#     for bus, files in ders_same_buses.items():
#         peaks_per_node = defaultdict(int)
#         for file in range(len(ders_same_buses[bus])):
#             pdm.read_demand_files(file=ders_same_buses[bus][file], data_dir=data_dir)
#             peaks_per_node = pdm.find_peak_demand(peaks_per_node=peaks_per_node, counter=counter)
#             max_ts, max_val, target_bus = pdm.get_daily_peaks(peaks_per_node=peaks_per_node, counter=counter)
#             peak_watts_and_times.append({target_bus:[max_ts,max_val]})
#         counter += 1
#     watts, time, targetd_bus = pdm.post_peak_demand_time(peak_watts_and_times=peak_watts_and_times)