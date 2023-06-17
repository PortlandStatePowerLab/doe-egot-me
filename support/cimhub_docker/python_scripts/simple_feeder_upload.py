import os
import cimhub.api as cimhub
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
class upload_feeder_blazegraph:

    def __init__(self):
        
        # Get Paths
        self.main_dir = os.getcwd()
        self.me_dir = '/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/'
        self.dss_dir = './dss/'
        self.glm_dir = './glm/'

        # Setup file names:
        self.dss_name = 'Master'

        # cimhub config files
        self.cfg_json = f'{self.main_dir}/cimhub_config_files/cimhubdocker.json'
    
    def get_blazegraph_link(self):
        CIMHubConfig.ConfigFromJsonFile (self.cfg_json)

    def remove_all_feeders(self):
        cimhub.clear_db (self.cfg_json)

    def upload_model_to_blazegraph(self):
        os.system(f'curl -D- -H "Content-Type: application/xml" --upload-file {self.main_dir}/dss/{self.dss_name}.xml -X POST {CIMHubConfig.blazegraph_url}')
    
    def list_feeders(self):
        cimhub.list_feeders (self.cfg_json)

if __name__ == '__main__':
    feeder = upload_feeder_blazegraph()
    feeder.get_blazegraph_link()
    feeder.upload_model_to_blazegraph()
    feeder.list_feeders()