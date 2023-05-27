import ast
from pprint import pprint as pp
import xml.etree.ElementTree as et
from collections import defaultdict



class mimic_meas_data:

    def __init__(self):
        self.phases = []
        self.mags = []
        self.bus = []

        self.data = defaultdict(list)

        with open ("../t30.txt", "r") as f:
            lines = f.readlines()

        for line in lines:
            self.filter_lines(line)

    
    def filter_lines (self, line):
        if line.startswith("{") or line.startswith(" "):
            self.get_mags(line)
            self.get_phases(line)
            self.get_buses(line)

    
    def get_buses (self, line):
        if line.startswith("{'B"):
            buses = line.strip("{'Bus': }").split("',")[0]
            if buses.startswith("tlx"):
                self.bus.append(buses)
    
    def get_phases (self, line):
        if line.startswith(" 'Phases'"):
            phase = line.strip(" 'Phases'").split(": '")[1].split("',")[0]
            if phase == "s1" or phase == "s2":
                self.phases.append(phase)
    
    def get_mags (self, line):
        if line.startswith(" 'magnitude'"):
            mg = line.strip(" 'magnitude'").split(": ")[1].split(",")[0]
            if float(mg) < 130:
                self.mags.append(mg)
    
    def modify_lists_lengs (self):
        self.bus = self.bus[:10]
        self.mags = self.mags[:10]
        self.phases = self.phases[:10]
    
    def get_buses_in_dict (self):
        for i in range(len(self.bus)):
            item1 = self.bus[i]
            item2 = self.phases[i]
            item3 = self.mags[i]

            self.data['grid service meas'].append((item1, item2, item3))
        pp(self.data)
        

# m = mimic_meas_data()
# m.modify_lists_lengs()
# m.get_buses_in_dict()

from collections import ChainMap as cp

class automatically_import_csip_topology:

    def __init__(self):


        self.level_analysis = {
            "goTopologyProcessor": {
                # "self.segments_list": {
                #     "function": ".get_segments()",
                #     "threshold": 2401
                # },
                # "self.feeders_list": {
                #     "function": ".get_feeders()",
                #     "threshold": 2401
                # },
                # "self.groups_list": {
                #     "function": ".get_groups()",
                #     "threshold": 2401
                # },
                "self.bus_list": {
                    "function": ".get_buses()",
                    "threshold": 120
                }
            }
        }

    def get_uncommented_topologies(self):

        for key, value in self.level_analysis.items():
            for clas, func in value.items():
                eval(f"{key}{func['function']}")

class read_services_schema:
    """
    It takes a lot of processing to get the right attributes for the right service.
    I think it is better to convert xml to dict and parse the dict. Sean, you were right.
    """
    def __init__(self):

        self.xml_file = "../manually_posted_service_input.xml"
    
    def read_file (self):
        self.tree = et.parse(self.xml_file)
        self.root = self.tree.getroot()
    
    def get_voltage_support_service (self):
        groups = self.get_elements (service_type='"Voltage service"')
        # return groups
    
    def get_elements (self, service_type):
        attributes = []
        if service_type == '"Voltage service"':
            for attributes in self.root.find('service3'):
                print(f"{attributes.tag} = {attributes.text}")
    
data = read_services_schema()
root = data.read_file()
data.get_voltage_support_service()
# voltage_service_atts = data.get_voltage_support_service()
# print(voltage_service_atts)
