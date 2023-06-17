import os
import csv
import json
import numpy as np
import pandas as pd
from datetime import datetime
from pprint import pprint as pp
from pathlib import Path as path

'''
This script creates DER-S Historical data input file for the ME. Before using script, the feeder
must be in a dss format (OpenDSS), and its coordinates file must be created.
'''

current_dir = path().absolute()

der_loc_files = '/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/cimhub_docker/psu_feeder_coords.csv'

nodes = ["680","633","632","692","675","671","684","645","652", "611"]

def create_df_headers(nodes):
    # This funcion creates headers that are equal to the number of the DERs (960) + Time col.
    header = ['Time'] + ['DER'+str(i)+'_mag' for i in range(1,961)] + ['DER'+str(i)+'_loc' for i in range(1,961)]
    df = pd.DataFrame(columns=header)
    df = pd.concat([df, pd.DataFrame(columns=header)], ignore_index=True)
    return df

def get_int(x):                     #Called in sort_list func. Not in main
    return int(x.split('_')[-1])

def sort_list(der_s_busses):        #Called in get_der_loc func. Not in main
    return sorted(der_s_busses, key=get_int)

def get_der_loc (der_loc_files, df_der_loc):
    '''
    This functions reads each DER bus location from the feeder coordinates file, 
    and appends it to a dictionary. The dictionary will be converted into a df 
    and then a CSV file later.
    '''
    der_s_busses = []
    df = pd.read_csv(der_loc_files, names = ['bus','x','y'])
    filtered_df = df[df['bus'].str.startswith("trip_load")]
    for node in nodes:
        for index, row in filtered_df.iterrows():
            if node in row.to_string():
                der_s_busses.append(row['bus'])
    der_s_busses = list(set(der_s_busses))
    der_s_busses = sort_list(der_s_busses)
    return der_s_busses
    
def read_csv_file (x):
    '''
    This function returns a one day data from the house profiles (960 profiles).
    '''
    df = pd.read_csv (x, names = ['timestamp','watts'])
    df = df.head(97)
    return df
    
def read_watts():
    '''
    This function reads a one-day data from each load profile, appends them to a DER in a 
    dictionary. At the end of this function, a dictionary will have all DERs location and their
    associated power values in Watts.
    '''
    csv_files = os.chdir('../../testing_glm/csv_files/')
    ders_values = []
    i = 0
    for files in (os.listdir(csv_files)):
        if files.startswith('house'):
            df = read_csv_file (files)
            for k, row in df.iterrows():
                ders_values.append(row["watts"])
    return ders_values

def sort_dict(der_s_busses, ders_values):
    dict = {}
    k = 97
    j = 0
    for i in range(len(der_s_busses)):
        dict[f"DER{i}_mag"] = ders_values[j:k]
        dict[f"DER{i}_loc"] = der_s_busses[i]
        j = k
        k += 97
    dict["Time"] = 999
    return dict

def create_df(der_s_dict):
    '''
    This function returns a DataFrame from the dictionary in the previous function. The 
    power values for each DER is in a list that conains a one-day worth of data. 
    (So each DER has only one row). The df.explode() function separates the list elements
    and puts them in rows.
    '''
    os.chdir(current_dir)
    df = pd.DataFrame.from_dict(der_s_dict)
    df = df.explode("DER0_mag")
    return df

def interpolate_df(df):
    '''
    The given power profiles have a 15-minutes time resolution. This function expands the 
    data into a one second time-resolution, fill in the missing DER_locations and DER_magnitudes.
    '''
    df["Time"] = pd.date_range('2023-01-01 00:00:00', '2023-01-02 00:00:00', freq = '15T')
    # df["Time"] = pd.to_datetime(df["Time"])
    # df['Time'] = (df['Time'].apply(lambda x: x.timestamp())).astype(int)
    # cols = df.columns.tolist()
    # cols.remove('Time')
    # cols = ['Time'] + cols
    # df = df[cols]
    # return df
    new_ts = pd.date_range('2023-01-01 00:00:00', '2023-01-02 00:00:00', freq = '1T')
    expanded_df = pd.concat([df.set_index('Time'), pd.DataFrame({'Time': new_ts}).set_index('Time')], axis=1, join='outer').ffill().reset_index()
    expanded_df['Time'] = pd.to_datetime(expanded_df['Time'])
    expanded_df['Time'] = (expanded_df['Time'].apply(lambda x: x.timestamp())).astype(int)
    return expanded_df
    


def wr_csv(df):
    # choosing only 4 columns
    # df = df.iloc[:, :5]
    float_cols = [col for col in df.columns if df[col].dtype == 'float64']
    df[float_cols] = df[float_cols].astype(int)
    # Choosing only 10 rows
    # df = df.head(5)
    # df = df.head(5400)
    df = df.applymap(lambda x: x.lower() if type(x) == str else x) # change all bus names to lower case to match blazegraph query
    os.chdir('/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/DERSHistoricalDataInput/')
    df.to_csv('psu_13_feeder_ders_s.csv', index=False)

def main(der_loc_files, nodes, current_dir):
    empty_df = create_df_headers(nodes)
    der_s_busses = get_der_loc (der_loc_files, empty_df)
    ders_values = read_watts()
    der_s_dict = sort_dict(der_s_busses, ders_values)
    df = create_df(der_s_dict)
    df = interpolate_df(df)
    wr_csv(df)
main(der_loc_files, nodes, current_dir)