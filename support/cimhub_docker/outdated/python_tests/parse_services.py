# go_topology_class_import_topology testing code:

import xmltodict
from pprint import pprint as pp

file = '/home/deras/Desktop/midrar_work_github/doe-egot-me/support/csip_topology/xml_output.xml'

def import_topology_from_file(file):

    with open (file, 'r', encoding='utf-8') as f:
        xml_file = f.read()
    
    topology = xmltodict.parse(xml_file)
   
    return topology

def get_group_members (topology):
    
    bus_list = [

    load for source, k in topology.items()
    for nodes in topology[source]
    for fed in topology[source][nodes]
    for seg in topology[source][nodes][fed]
    for xf in topology[source][nodes][fed][seg]
    for tls in topology[source][nodes][fed][seg][xf]
    for load in topology[source][nodes][fed][seg][xf][tls]
    ]

    bus_list = list(set(bus_list))

    return bus_list


def get_groups_bus_is_in(topology):

    groups = list(topology[list(topology.keys())[0]])
    return groups

def main(file):
    topology = import_topology_from_file(file)
    busses = get_group_members(topology)
    groups = get_groups_bus_is_in(topology)

main(file)