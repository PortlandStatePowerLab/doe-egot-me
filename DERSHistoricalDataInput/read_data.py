import os
import csv
import pandas as pd
from pprint import pprint as pp
from collections import defaultdict

df = pd.read_csv("./psu_feeder_ders_data.csv")

def expand_ders_file(df):
    counter = 0
    for i in range(1, len(df.columns), 2):
        new_df = df.iloc[:, [0,i,i+1]]
        new_df.to_csv(f'./ders_{counter}.csv', index=False)
        counter += 1

def test(df):
    ders_files = [file for file in os.listdir("./") if file.startswith("ders")]
    ders_files_sorted = sorted(ders_files, key=lambda x: int(x.split("_")[1].split(".")[0]))
    df_all = pd.read_csv(ders_files_sorted[0], usecols=['Time'])
    
    x = []

    for file in ders_files_sorted:
         df = pd.read_csv(file,usecols=[1,2])
         df_all = pd.concat([df_all, df], axis=1)
    
    for index, row in df_all.iterrows():
         row = dict(row)
         x.append(row)
    pp(x)

def drop_data(df):
    df = df.iloc[:, :3]
    return df
def main(df):
    expand_ders_file(df)
    # df = drop_data(df)
    # df.to_csv("./ders_new.csv", index=False)
    # test(df)

main(df)