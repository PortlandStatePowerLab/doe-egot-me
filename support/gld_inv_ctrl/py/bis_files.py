import ast
import glm
from pprint import pprint as pp

class add_battery_attributes ():

    def __init__(self):
        self.file_path = "../13_node_feeder/"
        self.file_name = "model_base.glm"
    

    def read_file (self):
        data = glm.load(self.file_path+self.file_name)
        return data
    
    def open_file (self):
        self.glm_file = open('./model_base_psu.glm', 'w')

    def get_inv_objects (self):
        self.data = self.read_file()
        self.open_file()
        for obj in self.data['objects']:
            if obj['name'].startswith("inv"):
                print(f"object inverter {{", file=self.glm_file)
                for j in obj['attributes']:
                    if j == 'V_base':
                        splitted = obj['attributes']['parent'].split("_s")[0]
                        obj['attributes'][j] = f"${{{splitted}}}"
                        self.return_attributes(j,obj['attributes'][j])
                    else:
                        self.return_attributes(j, obj['attributes'][j])
                self.return_attributes(attribute='V1',value='0.90')
                self.return_attributes(attribute='Q1',value='0.70')
                self.return_attributes(attribute='V2',value='0.95')
                self.return_attributes(attribute='Q2',value='0.0')
                self.return_attributes(attribute='V3',value='1.05')
                self.return_attributes(attribute='Q3',value='0.00')
                self.return_attributes(attribute='V4',value='1.10')
                self.return_attributes(attribute='Q4',value='-0.8')
                print(f"\tobject battery {{", file=self.glm_file)
                for i in obj['children']:
                    for k in i['attributes']:
                        print(f"\t\t{k} {i['attributes'][k]};", file=self.glm_file)
                print("\n\t};\n}",file=self.glm_file)
            
    def return_attributes (self, attribute, value):
        print(f"\t{attribute} {value};",file=self.glm_file)
        
    def define_inv_voltages (self):
        self.data = self.read_file()
        for obj in self.data['objects']:
            if obj['name'].startswith("inv"):
                splitted = obj['attributes']['parent'].split("_s")[0]
                print(f"#define {splitted}=240")
    
    def setup_recorders (self):
        self.data = self.read_file()
        rec_file = open('recorders.glm', 'w')
        counter = 0
        for obj in self.data['objects']:
            if obj['name'].startswith("inv"):
                bus_name = obj['attributes']['parent'].split("_s")[0]
                parent = obj['attributes']['parent']
                splitted = obj['attributes']['name'].split("_")
                rec_name = "_".join([splitted[4],splitted[5],splitted[6]])
                print(f"object recorder {{", file=rec_file)
                print(f"\tname rec_{rec_name};", file=rec_file)
                print(f"\tparent {parent};", file=rec_file)
                print(f"\tproperty measured_power.imag;", file=rec_file)
                print(f"\tfile ./gld_outputs/{bus_name}.csv;", file=rec_file)
                print(f"\tinterval 60;", file=rec_file)
                print(f"}};\n", file=rec_file)
        


file = add_battery_attributes()
# file.get_inv_objects()
file.setup_recorders()

