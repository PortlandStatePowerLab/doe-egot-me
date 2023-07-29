import csv
from pprint import pprint as pp


class establish_xy_coordinates():

    def __init__(self):

        # Reference file:
        self.dss_file = "../Master.dss"

        # Arrange nodes based on x-y plane levels

        self.x1_nodes = ["634","633","632","645", "646"]
        self.x2_nodes = ["675","692", "671","684", "611"]
        self.backbone_nodes = ["650","630" ,"6321","680"]
        self.all_nodes = ["630" ,"6321","632","671","680","684", "611","652","645", "646","692", "675","633", "634"]

        # Output file
        # self.coords_file = open ('psu_coords_test','w')


    def extract_busses (self):        
        self.bus_names = []
        with open (self.dss_file) as f:
            lines = f.readlines()
            for line in lines:
                for token in line.split():
                    if (token.startswith("Bus1")) or (token.startswith("bus")) or (token.startswith("bus1")) or (token.startswith("bus2")):
                        filtered_token = token.split('=')[1].split('.')[0]
                        if filtered_token not in self.bus_names: #Remove duplicated bus names
                            self.bus_names.append(filtered_token)

    def filter_busses_with_associated_objects(self):
        self.nodes_busses = {}
        for node in self.all_nodes:
            self.nodes_busses[node] = []
        
        for node in self.nodes_busses:
            for bus in self.bus_names:
                if node in bus:
                    self.nodes_busses[node].append(bus)
    
    def get_nodes(self,node,obj,x,y):
        for elem in obj:
            if elem.startswith('N6'):
                self.all_objects_coordinates[node].append(f'{elem},{x},{y}')
                

    def get_meters(self, node, obj,x,y):
        for elem in obj:
            if elem.startswith('meter'):
                self.all_objects_coordinates[node].append(f'{elem},{x},{y}')
                x -= 50

    def get_xfmr_meter(self, node, obj,x,y):
        for elem in obj:
            if elem.startswith('xfmr_meter'):
                self.all_objects_coordinates[node].append(f'{elem},{x},{y}')
                x -= 5

    def get_trip_node(self, node, obj,x,y):
        for elem in obj:
            if elem.startswith('trip_node'):
                self.all_objects_coordinates[node].append(f'{elem},{x},{y}')
                x -= 5
    
    def get_trip_load(self, node, obj,x,y):
        for elem in obj:
            if elem.startswith('tlx'):
                self.all_objects_coordinates[node].append(f'{elem},{x},{y}')
                x -= 8

    def vertical_obj(self):
        self.all_objects_coordinates = {}
        for node in self.all_nodes:
            self.all_objects_coordinates[node] = []

        for node, obj in self.nodes_busses.items():      
            if node == '633':
                self.get_nodes(node,obj,x=3750,y=900)
                self.get_meters(node, obj,x=3800,y=880)
                self.get_xfmr_meter(node, obj,x=3850,y=840)
                self.get_trip_node(node, obj,x=3850,y=800)
                self.get_trip_load(node, obj,x=4000,y=780)
            
            if node == '632': # The elements in this node include N6321 and N632
                self.get_nodes(node, obj,x=3000,y=900)
                self.get_meters(node, obj,x=3000,y=880)
                self.get_xfmr_meter(node, obj,x=3000,y=840)
                self.get_trip_node(node, obj,x=3000,y=800)
                self.get_trip_load(node, obj,x=3000,y=780)
            
            if node == '645':
                self.get_nodes(node, obj,x=2000,y=900)
                self.get_meters(node, obj,x=2000,y=880)
                self.get_xfmr_meter(node, obj,x=2000,y=840)
                self.get_trip_node(node, obj,x=2000,y=800)
                self.get_trip_load(node, obj,x=2000,y=780)

            if node == '646':
                self.get_nodes(node, obj,x=1300,y=900)
                self.get_meters(node, obj,x=1300,y=880)
                self.get_xfmr_meter(node, obj,x=1300,y=840)
                self.get_trip_node(node, obj,x=1300,y=800)
                self.get_trip_load(node, obj,x=1300,y=780)
            
            if node == '675':
                self.get_nodes(node,obj,x=3750,y=500)
                self.get_meters(node, obj,x=3800,y=480)
                self.get_xfmr_meter(node, obj,x=3850,y=440)
                self.get_trip_node(node, obj,x=3850,y=400)
                self.get_trip_load(node, obj,x=4000,y=380)
            
            if node == '692':
                self.get_nodes(node,obj,x=3040,y=500)
                self.get_meters(node, obj,x=3040,y=480)
                self.get_xfmr_meter(node, obj,x=3040,y=440)
                self.get_trip_node(node, obj,x=3040,y=400)
                self.get_trip_load(node, obj,x=3040,y=380)
            
            if node == '671':
                self.get_nodes(node,obj,x=2000,y=500)
                self.get_meters(node, obj,x=2000,y=480)
                self.get_xfmr_meter(node, obj,x=2000,y=440)
                self.get_trip_node(node, obj,x=2000,y=400)
                self.get_trip_load(node, obj,x=2000,y=380)
            
            if node == '684':
                self.get_nodes(node,obj,x=1020,y=500)
                self.get_meters(node, obj,x=1020,y=480)
                self.get_xfmr_meter(node, obj,x=1020,y=440)
                self.get_trip_node(node, obj,x=1020,y=400)
                self.get_trip_load(node, obj,x=1020,y=380)
            
            if node == '611':
                self.get_nodes(node,obj,x=380,y=500)
                self.get_meters(node, obj,x=380,y=480)
                self.get_xfmr_meter(node, obj,x=380,y=440)
                self.get_trip_node(node, obj,x=380,y=400)
                self.get_trip_load(node, obj,x=380,y=380)

            if node == '652':
                self.get_nodes(node,obj,x=1020,y=100)
                self.get_meters(node, obj,x=1020,y=80)
                self.get_xfmr_meter(node, obj,x=1020,y=40)
                self.get_trip_node(node, obj,x=1020,y=20)
                self.get_trip_load(node, obj,x=1020,y=5)
            
            if node == '680':
                self.get_nodes(node,obj,x=2000,y=100)
                self.get_meters(node, obj,x=2000,y=80)
                self.get_xfmr_meter(node, obj,x=2000,y=40)
                self.get_trip_node(node, obj,x=2000,y=20)
                self.get_trip_load(node, obj,x=2000,y=5)
                


        self.all_objects_coordinates['SourceBus'] = [('SourceBus,3000,1000')]
        self.all_objects_coordinates['transformer'] = [('trans_source_N650,3000,990')]
        self.all_objects_coordinates['transformer'] = [('XFM1,3850,900')]
        self.all_objects_coordinates['650'] = [('N650,3000,985')]
        # self.all_objects_coordinates['630'].append('N630,2000,940')
        self.all_objects_coordinates['reg'] = [('Reg,3000,980')]
        self.all_objects_coordinates['reg60'] = [('RG60,3000,975')]
        self.all_objects_coordinates['634'].append('N634,4000,900')
        self.all_objects_coordinates['6321'].append('N6321,2000,750')
        
        
    def wr_csv(self):
        with open ('./psu_feeder_coordinates.csv','w', newline='') as output:
            writer = csv.writer(output)
            for key, values in self.all_objects_coordinates.items():
                for value in values:
                    writer.writerow(value.split(','))

if __name__ == '__main__':
    xy = establish_xy_coordinates()
    xy.extract_busses()
    xy.filter_busses_with_associated_objects()
    xy.vertical_obj()
    xy.wr_csv()
