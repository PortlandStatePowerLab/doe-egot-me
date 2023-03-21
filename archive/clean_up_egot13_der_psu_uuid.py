import pandas as pd
import csv
import pprint
path = "./DERScripts/"

read_file = open(path+'archive/EGoT13_der_psu_uuid.txt','r')
write_file = open(path+'EGoT13_der_psu_uuid.txt', 'w')

reader = csv.reader(read_file)
writer = csv.writer(write_file)

for i in reader:
    if 'BatteryUnit' in i or 'Location' in i or 'Terminal' in i:
        writer.writerow(i)