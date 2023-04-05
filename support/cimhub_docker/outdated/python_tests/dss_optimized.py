import csv
import pandas as pd

dss_path = "/home/deras/Desktop/midrar_work_github/doe-egot-me/support/cimhub_docker/python_scripts/optimized_dss/Master.dss"
node = ['680','633','632','692','675', '671', '684' ,'652', '645', '611']
nodes = []
counter = 0
new_load_busses = []
load_1 = []
load_2 = []

with open (dss_path, 'r') as f:
    data = f.read()
lines = data.split('\n')
for line in lines:
    if line.startswith('~ bus1=trip_node'):
        line = line.split('~ ')[1]
        new_load_busses.append(line)

    if line.startswith('New storage'):
        load_1.append(line.split(' Bus1=')[0])
        load_2.append(line.split('1.2 ')[1])
        nodes.append(((line.split(' Bus1=')[0]).split('load_')[1]).split('_')[0])



for i in node:
    for bus in new_load_busses:
        if i in bus:
            print(bus)

# for i in range(len(load_1)):
#     if (nodes[i] in load_1[i]) and (nodes[i] in new_load_busses[i]):
#         print(f'{load_1[i]} {new_load_busses[i]}')

#         counter += 1
#         print(i)
