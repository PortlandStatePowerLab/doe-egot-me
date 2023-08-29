import os
import csv
import time
import pandas as pd
from pprint import pprint as pp
from collections import defaultdict
class update_rwhders:

    def __init__(self):

        self.me_dir = os.path.dirname(os.getcwd())
        self.bus_profile = self.me_dir+'/support/config_files/DERs_full_list.txt'

    def get_buses (self):
        df = pd.read_csv(self.bus_profile, skiprows=3)
        self.bus_list = df.iloc[:,1].to_list()

    def create_dict(self):
        self.profiles = defaultdict(int)

    def get_files (self):
        ders_files = [file for file in os.listdir(rwh.me_dir+'/ders_testing/')]
        self.ders_files = sorted(ders_files, key=lambda x: int(x.split("_")[1].split(".")[0]))
    
    def post_values(self):
        try:
            row = next(reader)
            for i in range(len(self.bus_list)):
                ders_files = open(f'../RWHDERS_Inputs/DER000{i}_Bus{self.bus_list[i]}.csv','w')
                print(f'P,{row[1]}', file=ders_files)
            self.read_all_files = False
        except StopIteration:
            pass
    
    def checkpoint(self):
        if self.read_all_files:
            quit()
        print('sleeping ..')
        time.sleep(10)

if __name__ == '__main__':
    rwh = update_rwhders()
    rwh.get_buses()
    rwh.create_dict()
    rwh.get_files()

    index = 0
    while True:
        read_all_files = True
        for i in range(len(rwh.ders_files)):
            with open (rwh.me_dir+'/ders_testing/'+rwh.ders_files[i], newline='') as f:
                reader = csv.reader(f)
                headers = next(reader)
                for ind in range(index):
                    next(reader)
                rwh.post_values()

        rwh.checkpoint()
        index += 1