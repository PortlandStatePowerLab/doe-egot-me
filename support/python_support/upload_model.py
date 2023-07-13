import os
import subprocess
import cimhub.api as cimhub
import xml.etree.ElementTree as et
import cimhub.CIMHubConfig as CIMHubConfig

'''
 - This script uploads a customized IEEE-13 Node Feeder to GridAPPS-D Blazegraph. 
 - The Blazegraph contains several feeders. This script deletes all other feeders and upload only the IEEE 13-Node Feeder.
 - If you'd like to keep the other feeders, comment out remove_all_feeders() in main.
'''
class upload_feeder_blazegraph:

    def __init__(self):
        
        # Set Path
        self.main_dir = os.getcwd()

        # Setup file names:
        self.dss_name = 'Master'

        # cimhub config files
        self.cfg_json = f'{self.main_dir}/cimhubdocker.json'
    
    def get_blazegraph_link(self):
        CIMHubConfig.ConfigFromJsonFile (self.cfg_json)

    def remove_all_feeders(self):
        cimhub.clear_db (self.cfg_json)

    def upload_model_to_blazegraph(self):
        os.system(f'curl -D- -H "Content-Type: application/xml" --upload-file ../dss_files/{self.dss_name}.xml -X POST {CIMHubConfig.blazegraph_url}')
    
    def list_feeders(self):
        cimhub.list_feeders (self.cfg_json)

# The following is for testing. Remove later.

class configuration_files:

    def __init__(self):
        self.destination = "./"
        self.me_dir = "../"
        self.namespace = {"cim": "http://iec.ch/TC57/CIM100#"}
        self.der_name = {}
        self.der_loc = {}
        self.der_ter = {}
        self.pec = {}
    
    def read_xml_file(self):
        tree = et.parse('../dss_files/Master.xml')
        self.root = tree.getroot()
    
    def get_geo_region(self):
        for rgn in self.root.findall(".//cim:GeographicalRegion", self.namespace):
            self.rgn_mrid = rgn.find(".//cim:IdentifiedObject.mRID", self.namespace).text
    
    def get_sub_geo_region(self):
        for sub in self.root.findall(".//cim:SubGeographicalRegion", self.namespace):
            self.sub_mrid = sub.find(".//cim:IdentifiedObject.mRID", self.namespace).text
    
    def get_line_mrid(self):
        for line in self.root.findall(".//cim:Feeder", self.namespace):
            self.line_mrid = line.find(".//cim:IdentifiedObject.mRID", self.namespace).text

    def list_measurements (self):
        list_meas = open("./list_measurements.sh","w")
        print(f"python3 ListMeasureables.py cimhubconfig.json psu_13_node_feeder {self.line_mrid} Meas",
              file=list_meas)
        
        os.chmod("list_measurements.sh",0o755)
    
    def insert_houses(self):
        houses = open("./insert_houses.sh")
        print(f"python3 InsertHouses.py cimhubconfig.json {self.line_mrid} 1",
              file=houses)
        
        os.chmod("insert_houses.sh",0o755)
    
    def get_objects_name_and_mrid(self, elem):# Not in main
        name = elem.find(".//cim:IdentifiedObject.name", self.namespace).text
        mRID = elem.find(".//cim:IdentifiedObject.mRID", self.namespace).text
        return name, mRID

    def create_orig_der_config_file(self):

        for der in self.root.findall(".//cim:BatteryUnit", self.namespace):
            name, mrid = self.get_objects_name_and_mrid(elem=der)
            self.der_name[name] = mrid
        
        for pec in self.root.findall(".//cim:PowerElectronicsConnection", self.namespace):
            name, mrid = self.get_objects_name_and_mrid(elem=pec)
            self.pec[name] = mrid

        for terminal in self.root.findall(".//cim:Terminal", self.namespace):
            if terminal.find(".//cim:IdentifiedObject.name", self.namespace).text.startswith("trip_load"):
                name, mrid = self.get_objects_name_and_mrid(elem=terminal)
                self.der_ter[name] = mrid
        
        for loc in self.root.findall(".//cim:Location", self.namespace):
            if loc.find(".//cim:IdentifiedObject.name", self.namespace).text.startswith("trip_load"):
                name, mrid = self.get_objects_name_and_mrid(elem=loc)
                self.der_loc[name] = mrid
    
    def write_orig_der_file(self):
        der_file = open("EGoT13_orig_der_psu.txt","w")
        for i in list(self.der_name.keys()):
            print(f"PowerElectronicsConnection,{i},{self.pec[i]}", file=der_file)
            print(f"BatteryUnit,{i},{self.der_name[i]}", file=der_file)
            location = f'{i}_Loc'
            print(f"Location,{location},{self.der_loc[location]}", file=der_file)
            terminal = f'{i}_T1'
            print(f"Terminal,{terminal},{self.der_ter[terminal]}", file=der_file)
        der_file.close()

    def sim_config_file(self):
        config_file = open("../Configuration/simulation_configuration.txt","w")
        sim_config_file = f'''{{
    "power_system_config": {{
        "GeographicalRegion_name": "{self.rgn_mrid}",
        "SubGeographicalRegion_name": "{self.sub_mrid}",
        "Line_name": "{self.line_mrid}"
    }},
    "application_config": {{
        "applications": []
    }},
    "simulation_config": {{
        "start_time": "1672531200",
        "duration": "120",
        "simulator": "GridLAB-D",
        "timestep_frequency": "1000",
        "timestep_increment": "1000",
        "run_realtime": "true",
        "simulation_name": "psu_13_node_feeder",
        "power_flow_solver_method": "NR",
        "model_creation_config": {{
            "load_scaling_factor": "1",
            "schedule_name": "ieeezipload",
            "z_fraction": "0",
            "i_fraction": "1",
            "p_fraction": "0",
            "randomize_zipload_fractions": "false",
            "use_houses": "True"
        }}
    }}
}}
        '''
        print(sim_config_file, file=config_file)

    def publish_files(self):
        self.read_xml_file()
        self.get_geo_region()
        self.get_sub_geo_region()
        self.get_line_mrid()
        self.list_measurements()
        self.insert_houses()
        self.create_orig_der_config_file()
        self.sim_config_file()
        self.write_orig_der_file()

if __name__ == '__main__':
    feeder = upload_feeder_blazegraph()
    xml = configuration_files()
    feeder.get_blazegraph_link()
    feeder.remove_all_feeders()
    feeder.upload_model_to_blazegraph()
    feeder.list_feeders()