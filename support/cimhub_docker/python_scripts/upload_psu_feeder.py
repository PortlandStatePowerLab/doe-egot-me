import os
import sys
import json
import shutil
import argparse
import subprocess
import cimhub.api as cimhub
from pprint import pprint as pp
from gridappsd import GridAPPSD
from gridappsd import topics as t
import cimhub.CIMHubConfig as CIMHubConfig

'''
This script uploads a customized IEEE-13 Node Feeder to GridAPPS-D Blazegraph. 

Feeder Properties:
    
    1- The feeder is designed to handle approximately 1000 loads.
    2- Each load is customized with several home appliances (dishwashers, water heaters, etc)
    3- The feeder is tested to run without overloading issues for a week.
    4- The feeder is originally designed in GridLAB-D. It was then converted to OpenDSS.

Script main functionalities:

    1- Uploads the feeder to the Blazegraph.
    2- Creates testing scripts to compare the powerflow of the GridLAB-D and OpenDSS 
    versions of the feeder.
    3- Creates the needed configuration files and historical data to run the Modeling Environment (ME)

'''
class upload_feeder_blazegraph():

    def __init__(self):
        
        # Get Paths
        self.main_dir = os.getcwd()
        self.me_dir = '/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/'
        self.dss_dir = './dss/'
        self.glm_dir = './glm/'

        # Set up exported files folders
        # path('dss').mkdir(parents=False, exist_ok=True)
        # path('glm').mkdir(parents=False, exist_ok=True)

        # Setup file names:
        self.dss_name = 'Master'

        # OS Compatibility:
        if sys.platform == 'win32':
            self.shfile_glm = './glm/checkglm.bat'
            self.shfile_run = 'checkglm.bat'
            self.cfg_json = 'cimhubjar.json'
        else:
            self.shfile_glm = './glm/checkglm.sh'
            self.shfile_run = './checkglm.sh'
            self.cfg_json = f'{self.main_dir}/cimhub_config_files/cimhubdocker.json'
    
    def get_blazegraph_link(self):
        CIMHubConfig.ConfigFromJsonFile (self.cfg_json)

    def remove_all_feeders(self):
        cimhub.clear_db (self.cfg_json)

    def upload_model_to_blazegraph(self):
        os.system(f'curl -D- -H "Content-Type: application/xml" --upload-file {self.main_dir}/dss_no_loads/{self.dss_name}.xml -X POST {CIMHubConfig.blazegraph_url}')
    
    def list_feeders(self):
        cimhub.list_feeders (self.cfg_json)
  

class dss_configuration_file (upload_feeder_blazegraph):
    
    def __init__(self):

        super().__init__()  #Inherit all variables in upload_feeder_blazegraph class

        # Set file names:
        self.setting_file_name = 'cim_test.dss'


    def connect_to_gridappsd(self):
        
        os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
        os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
        os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
        os.environ['GRIDAPPSD_PORT'] = '61613'
        self.gapps_session = GridAPPSD()
        assert self.gapps_session.connected
    
    def set_query(self):
        # NOT CALLED IN MAIN. CALLED IN get_mrids FUNC.
        message = {
        "requestType": "QUERY_MODEL_INFO",
        "resultFormat": "JSON"
        }
        return message
    
    def get_query_response(self, message):
        # NOT CALLED IN MAIN. CALLED IN get_mrids FUNC.
        topic = t.REQUEST_POWERGRID_DATA
        query_resp = self.gapps_session.get_response(topic, message)
        return query_resp

    def get_mrids (self):

        query_resp = self.get_query_response(self.set_query())
        
        for i in range(len(query_resp['data']['models'])):
            if query_resp['data']['models'][i]['modelName'].startswith('psu_'):
                self.mrids = {
                    'line_name':query_resp['data']['models'][i]['modelId'],
                    'geo_rgn':query_resp['data']['models'][i]['regionId'],
                    'sub_rgn':query_resp['data']['models'][i]['subRegionId'],
                    'simulation_name':query_resp['data']['models'][i]['modelName']
                    }
        return self.mrids
        
    def OpenDSS_Settings(self):

        self.cases = [
            {'dssname':self.dss_name, 'root':self.dss_name, 'mRID':f"{self.mrids['line_name']}",
             'substation':'Fictitious', 'region':'Oregon', 'subregion':'Portland', 'skip_gld': False,
             'glmvsrc': 2400, 'bases':[208, 480, 2400, 4160], 'export_options':' -l=1.0 -p=1.0 -e=carson',
             'check_branches':[{'dss_link': 'Transformer.T633-634', 'dss_bus': 'N633'},
                               {'dss_link': 'Line.OL632-6321', 'dss_bus': 'N632'},
                               {'gld_link': 'xf_t633-634', 'gld_bus': 'n633'}]},
                    ]

    def export_dss_test_file(self):
        
        os.chdir(self.dss_dir)

        cim_test = open(f'{self.setting_file_name}', 'w')
        for row in self.cases:
            dssname = row['dssname']
            root = row['root']
            self.mRID = row['mRID']
            sub = row['substation']
            subrgn = row['subregion']
            rgn = row['region']
            print (f'redirect {dssname}.dss', file=cim_test)
            print (f'solve', file=cim_test)
            print (f'export cim100 substation={sub} subgeo={subrgn} geo={rgn} file={root}.xml', file=cim_test)
            print (f'export uuids {root}_uuids.dat', file=cim_test)
            print (f'export summary   {root}_s.csv', file=cim_test)
            print (f'export voltages  {root}_v.csv', file=cim_test)
            print (f'export currents  {root}_i.csv', file=cim_test)
            print (f'export taps      {root}_t.csv', file=cim_test)
            print (f'export nodeorder {root}_n.csv', file=cim_test)
            
        cim_test.close ()

    def run_opendss_file(self):
        p1 = subprocess.Popen(f'dss {self.setting_file_name}', shell=True)
        p1.wait()
    
    def create_glm_dss(self):
        os.system(f'java -cp "../target/libs/*:../target/cimhub-0.0.1-SNAPSHOT.jar" gov.pnnl.gridappsd.cimhub.CIMImporter -s={self.mRID} -u={CIMHubConfig.blazegraph_url} -o=both -l=1.0 -i=1 -h=0 -x=0 -t=1 master')
        
        # CIMHUB exports both glm and dss files in one folder. A bit of org in the next line:
        try:
            shutil.move('master_base.glm',f'{self.main_dir}/glm/')
        except shutil.Error:
            print('master_base.glm file is already in place!')
            
        os.chdir(self.main_dir)


class gld_configuration_file(upload_feeder_blazegraph):

    def __init__(self):
        
        super().__init__() 

        # Set base GridLAB-D file:
        self.setting_file_name = 'master_run.glm'       


    def GirdLABD_Settings(self):
        os.chdir(self.glm_dir)
        '''
        The settings below are set constant for many reasons. For example, GridAPPS-D currently
        only runs NR method. The same applies for the other settings. Most of these constraints
        are set by GridAPPS-D
        '''
        glm_run = open(f'{self.setting_file_name}', 'w')
        
        print("clock {\n\ttimezone EST+5EDT;\n\tstarttime '2000-01-01 0:00:00';\n\tstoptime '2000-01-01 0:00:00';\n};", file=glm_run)
        print('#set relax_naming_rules=1\n#set profiler=1', file=glm_run)
        print("module powerflow {\n\tsolver_method NR;\n\tline_capacitance TRUE;\n};", file=glm_run)
        print("module climate;\nmodule generators;\nmodule tape;\nmodule reliability {\n\treport_event_log false;\n};", file=glm_run)
        print("object climate {\n\tname climate;\n\tlatitude 45.0;\n\tsolar_direct 93.4458;\n}", file=glm_run)
        print('#define VSOURCE=2400\n#include "master_base.glm";\n#ifdef WANT_VI_DUMP\n', file=glm_run)
        print("object voltdump {\n\tfilename Master_volt.csv;\n\tmode POLAR;\n};", file=glm_run)
        print("object currdump {\n\tfilename Master_curr.csv;\n\tmode POLAR;\n};", file=glm_run)
        print("#endif", file=glm_run)

        glm_run.close()
    
    def run_glm_file(self):
        p1 = subprocess.Popen(f'gridlabd {self.setting_file_name}', shell=True)
        p1.wait()
        os.chdir(self.main_dir)
    
class me_configuration_files (dss_configuration_file):

    def __init__(self):
        
        super().__init__()
        
        # ME Simulation Configuration parameters:
        self.simulation_duration = "21600"

        # Set paths:
        # self.me_dir = '/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/'

    
    def set_me_simulation_config_file (self):
        
        super().connect_to_gridappsd()

        self.mrids = super().get_mrids()

        self.sim_config = {
            "power_system_config": {
            "GeographicalRegion_name":self.mrids['geo_rgn'],
            "SubGeographicalRegion_name":self.mrids['sub_rgn'],
            "Line_name":self.mrids['line_name']
            },
            "application_config": {
            "applications": []
            },
            "simulation_config": {
            "start_time": "1672531200",
            "duration": self.simulation_duration,
            "simulator": "GridLAB-D",
            "timestep_frequency": "1000",
            "timestep_increment": "1000",
            "run_realtime": "true",
            "simulation_name": self.mrids['simulation_name'],
            "power_flow_solver_method": "NR",
            "model_creation_config": {
                "load_scaling_factor": "1",
                "schedule_name": "ieeezipload",
                "z_fraction": "0",
                "i_fraction": "1",
                "p_fraction": "0",
                "randomize_zipload_fractions": "false",
                "use_houses": "false"
            }
        },
    }
        
    def write_files_to_directory (self):

        os.chdir(f'{self.me_dir}/Configuration/')

        with open ('simulation_configuration.json', 'w') as output:
            json.dump(self.sim_config, output, indent=4)
        
        os.chdir(self.main_dir)

class user_args_response():
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='\n\n'
                                     , usage=""" %(prog)s [options]\n\nInstructions:\n
                                     \n1- python3 upload_model.py -u\t--->\tonly upload the model to Blazegraph
                                     \n2- python3 upload_model.py -fdb\t--->\tupload model and keep feeders in the Blazegraph
                                     \n3- python3 upload_model -f\t--->\tRemoves the feeders in the Blazegraph and uploads the feeder\n""")
    
    
        self.parser.add_argument('-u','--upload-feeder',dest='upload_feeder', action ='store_true', help='Only upload feeder to Blazegraph')
        self.parser.add_argument('-fdb','--full-setup',dest='full_setup', action ='store_true', help='upload feeder and keep Feeders in Blazegraph')
        self.parser.add_argument('-f','--full-setup-clear-db',dest= 'full_setup_clear_db',action ='store_true', help='upload feeder and remove Feeders in Blazegraph')
        
        self.args = self.parser.parse_args()

        print(self.args)
    
    def global_classes(self):

        global feeder
        feeder = upload_feeder_blazegraph()
        global dss
        dss = dss_configuration_file()
        global gld
        gld = gld_configuration_file()
        global me
        me = me_configuration_files()
    
    def u_user_response(self):

        print('Uploading feeder ... ')
        feeder.get_blazegraph_link()
        feeder.upload_model_to_blazegraph()
        feeder.list_feeders()
    
    def fdb_user_response(self):

        print('Creating OpenDSS Files ...')

        self.u_user_response()
        dss.connect_to_gridappsd()
        dss.get_mrids()
        dss.OpenDSS_Settings()
        dss.export_dss_test_file()
        dss.run_opendss_file()
        dss.create_glm_dss()


        print('Creating GridLAB-D Files ...')

        gld.GirdLABD_Settings()
        gld.run_glm_file()
        
        print('Exporting ME Files ...')

        me.set_me_simulation_config_file()
        me.write_files_to_directory()

    def f_user_response(self):
        feeder.remove_all_feeders()
        self.fdb_user_response()
    
    def execute_script(self):
        if self.args.upload_feeder:
            self.u_user_response()

        if self.args.full_setup:
            self.fdb_user_response()

        if self.args.full_setup_clear_db:
            self.f_user_response()


if __name__ == '__main__':

    arg = user_args_response()
    arg.global_classes()
    arg.execute_script()