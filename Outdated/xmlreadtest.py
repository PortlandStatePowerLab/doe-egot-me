import xml.etree.ElementTree as ET

tree = ET.parse('../Configuration/topology.xml')
root = tree.getroot()
topology_map = []
for i, val in enumerate(root):
    topological_input_row_key = list(root[i].attrib.values())[0]
    topological_input_row_vals = []
    for a,b in enumerate(root[i]):
        topological_input_row_vals.append(list(root[i][a].attrib.values()))
    topology_map_row = {topological_input_row_key: topological_input_row_vals}
    topology_map.append(topology_map_row)


print(topology_map)
group_list = []
bus_list = []

for i in topology_map:
    group_list.append(list(i.keys())[0])
    bus_list.append(list(i.values()))

print(group_list)

for flatten_count in range(0,3):
    bus_list = [x for l in bus_list for x in l]

bus_list_final = []
[bus_list_final.append(x) for x in bus_list if x not in bus_list_final]
print(bus_list_final)
z = 'group-1'

for i in topology_map:
    try:
        bus_return = i[z]
        bus_return = [x for l in bus_return for x in l]
        print(bus_return)
    except KeyError:
        pass
