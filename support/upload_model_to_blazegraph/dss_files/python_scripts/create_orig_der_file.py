import cimhub.api as cimhub
from pprint import pprint as pp
import xml.etree.ElementTree as et

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
        self.pec = {}
    

    def read_xml_file(self):
        tree = et.parse(self.dss_files_dir+'Master.xml')
        self.root = tree.getroot()


    def grab_objects(self, obj_type, cim_type, identified_obj_name, identified_obj_mrid, namespace):
        
        for obj_type in self.root.findall(cim_type, namespace):
            name = obj_type.find(identified_obj_name, namespace).text
            mrid = obj_type.find(identified_obj_mrid, namespace).text


    def create_orig_der_file(self):
        namespace = {"cim": "http://iec.ch/TC57/CIM100#"}
        self.read_xml_file()

        for der in self.root.findall(".//cim:BatteryUnit", namespace):
            name = der.find(".//cim:IdentifiedObject.name", namespace).text
            mRID = der.find(".//cim:IdentifiedObject.mRID", namespace).text
            self.der_name[name] = mRID
        
        for pec in self.root.findall(".//cim:PowerElectronicsConnection", namespace):
            name = pec.find(".//cim:IdentifiedObject.name", namespace).text
            mRID = pec.find(".//cim:IdentifiedObject.mRID", namespace).text
            self.pec[name] = mRID

        for terminal in self.root.findall(".//cim:Terminal", namespace):
            if terminal.find(".//cim:IdentifiedObject.name", namespace).text.startswith("trip_load"):
                t_name = terminal.find(".//cim:IdentifiedObject.name", namespace).text
                t_mrid = terminal.find(".//cim:IdentifiedObject.mRID", namespace).text
                self.der_ter[t_name] = t_mrid
                # self.der_name[t_name] = t_mrid
        
        for loc in self.root.findall(".//cim:Location", namespace):
            if loc.find(".//cim:IdentifiedObject.name", namespace).text.startswith("trip_load"):
                loc_name = loc.find(".//cim:IdentifiedObject.name", namespace).text
                loc_mrid = loc.find(".//cim:IdentifiedObject.mRID", namespace).text
                self.der_loc[loc_name] = loc_mrid
                # self.der_name[loc_name] = loc_mrid
    
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
            
        

    
    

dss = create_der_and_non_der_config_files()
dss.create_orig_der_file()
dss.write_orig_der_file()