import pandas as pd
import os
class volt_drop:

    def __init__(self):

        self.path = "../"
        self.node = "633"
        self.destination = "../ders_testing2/"

    def read_files(self, file):

        self.df = pd.read_csv(self.path+'ders_testing/'+ file)
    
    def get_633_files (self):

        for index, row in self.df.iterrows():
            if self.node in row[3]:
                row[1] = 4500
            



v = volt_drop()
for file in os.listdir(v.path+'ders_testing/'):
    v.read_files(file)
    v.get_633_files()