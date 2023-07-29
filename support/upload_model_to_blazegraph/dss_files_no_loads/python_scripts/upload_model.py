import os
import subprocess
import pandas as pd
import cimhub.api as cimhub
from pprint import pprint as pp
import xml.etree.ElementTree as et
import cimhub.CIMHubConfig as CIMHubConfig

class set_up_blazegraph:

    def __init__(self):
        
        #Set DSS file name
        self.dss_name = 'Master'
        
        #Set Paths
        self.cfg_json = './cimhub_config_files/cimhubdocker.json'
    
    def get_blazegraph_link (self):
        CIMHubConfig.ConfigFromJsonFile (self.cfg_json)

    def remove_feeders (self):
        cimhub.clear_db (self.cfg_json)

    def upload_model(self):
        os.system(f'curl -D- -H "Content-Type: application/xml" --upload-file ../{self.dss_name}.xml -X POST {CIMHubConfig.blazegraph_url}')
    
    def list_feeders(self):
        cimhub.list_feeders (self.cfg_json)

model = set_up_blazegraph()
model.get_blazegraph_link()
model.remove_feeders()
model.upload_model()
model.list_feeders()

class create_der_and_non_der_config_files:

    def __init__(self):
        
        # Set Paths:
        self.dss_files_dir = "../"
        # self.destinations = "/home/deras/Desktop/midrar_work_github/doe-egot-me/DERScripts/"
        self.destinations = "./"
        # self.fully_loaded_dss_path = "/home/deras/Desktop/midrar_work_github/doe-egot-me/support/upload_model_to_blazegraph/dss_files/"

        #Set user preferences:
        self.num_der_needed = 10
        self.num_non_der_needed = 10

        #Set loads lists:
        self.der_name = {}
        self.der_loc = {}
        self.der_ter = {}
    

    def read_xml_file(self):
        tree = et.parse(self.dss_files_dir+set_up_blazegraph().dss_name+".xml")
        self.root = tree.getroot()


    def grab_objects(self, obj_type, cim_type, identified_obj_name, identified_obj_mrid, namespace):
        
        for obj_type in self.root.findall(cim_type, namespace):
            name = obj_type.find(identified_obj_name, namespace).text
            mrid = obj_type.find(identified_obj_mrid, namespace).text


    def create_orig_der_file(self):
        namespace = {"cim": "http://iec.ch/TC57/CIM100#"}
        self.read_xml_file()

        for energy_consumer in self.root.findall(".//cim:EnergyConsumer", namespace):
            name = energy_consumer.find(".//cim:IdentifiedObject.name", namespace).text
            mRID = energy_consumer.find(".//cim:IdentifiedObject.mRID", namespace).text
            self.der_name[name] = mRID

        for terminal in self.root.findall(".//cim:Terminal", namespace):
            if terminal.find(".//cim:IdentifiedObject.name", namespace).text.startswith("house"):
                t_name = terminal.find(".//cim:IdentifiedObject.name", namespace).text
                t_mrid = terminal.find(".//cim:IdentifiedObject.mRID", namespace).text
                self.der_ter[t_name] = t_mrid
                # self.der_name[t_name] = t_mrid
        
        for loc in self.root.findall(".//cim:Location", namespace):
            if loc.find(".//cim:IdentifiedObject.name", namespace).text.startswith("house"):
                loc_name = loc.find(".//cim:IdentifiedObject.name", namespace).text
                loc_mrid = loc.find(".//cim:IdentifiedObject.mRID", namespace).text
                self.der_loc[loc_name] = loc_mrid
                # self.der_name[loc_name] = loc_mrid
    
    def write_orig_der_file(self):
        der_file = open("EGoT13_orig_der_psu.txt","w")
        for i in list(self.der_name.keys()):
            print(f"EnergyConsumer,{i},{self.der_name[i]}", file=der_file)
            location = f'{i}_Loc'
            print(f"Location,{location},{self.der_loc[location]}", file=der_file)
            terminal = f'{i}_T1'
            print(f"Terminal,{terminal},{self.der_ter[terminal]}", file=der_file)
            
        

    
    

# dss = create_der_and_non_der_config_files()
# dss.create_orig_der_file()
# dss.write_orig_der_file()



    # def get_der_names (self, line):
    #     return line.split('.')[1].split(' ')

    # def grab_loads_buses(self):
    #     with open (self.fully_loaded_dss_path+set_up_blazegraph().dss_name+'.dss', 'r') as dss:
    #         contents = dss.readlines()
    #         for line in contents:
    #             if line.startswith("New storage."):

    #                 self.ders.append(self.get_der_names(line=line)[0])
    #                 self.buses.append(self.get_der_names(line=line)[2].split('=')[1])

    #             if line.startswith("New Load."):

    #                 self.none_ders.append(self.get_der_names(line=line)[0])
    #                 self.phases.append((self.get_der_names(line=line)[0].split('_')[2]).upper())

    # def create_der_files (self):
    #     headers = pd.DataFrame({'uuid_file':['EGoT13_der_psu_uuid.txt'], 'feederID':['fd_mrid']}, index=[0])
    #     self.write_der_files(data = headers, wr_mode="w")

    #     # ders = pd.DataFrame({'//name':self.ders,'bus':self.buses,'phases(ABCs1s2)':'s1s2',
    #     #                      'type(Battery,Photovoltaic)':'battery', 'RatedkVA': 24,'RatedkV':0.240,
    #     #                      'kW':0,'kVAR':0,'RatedkWH': 7.0,'StoredkWH': 7.0})
    #     # self.write_der_files(data=ders, wr_mode="a")

    #     none_ders = pd.DataFrame({'//name':self.none_ders,'bus':self.buses,'phases(ABCs1s2)':self.phases,
    #                          'type(Battery,Photovoltaic)':'battery', 'RatedkVA': 24,'RatedkV':0.240,
    #                          'kW':0,'kVAR':0,'RatedkWH': 7.0,'StoredkWH': 7.0})

    #     self.write_der_files(data=none_ders, wr_mode="a")
        

    # def write_der_files (self, data ,wr_mode):
    #     data.to_csv(f'{self.destinations}EGoT13_der_psu.txt', mode =wr_mode, index=False)


# dss = create_der_and_non_der_config_files()
# dss.grab_loads_buses()
# dss.create_der_files()