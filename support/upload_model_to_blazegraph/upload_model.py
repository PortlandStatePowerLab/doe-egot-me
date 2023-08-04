import os
import subprocess
import cimhub.api as cimhub
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
        self.cfg_json = f'{self.main_dir}/cimhub_config_files/cimhubdocker.json'
    
    def get_blazegraph_link(self):
        CIMHubConfig.ConfigFromJsonFile (self.cfg_json)

    def remove_all_feeders(self):
        cimhub.clear_db (self.cfg_json)

    def upload_model_to_blazegraph(self):
        os.system(f'curl -D- -H "Content-Type: application/xml" --upload-file {self.main_dir}/dss_files/{self.dss_name}.xml -X POST {CIMHubConfig.blazegraph_url}')
    
    def list_feeders(self):
        cimhub.list_feeders (self.cfg_json)

    def insert_der_and_measurements(self):
        os.chdir("./measurements/")
        p1 = subprocess.Popen('./run_measurements.sh', shell=True)
        p1.wait()

if __name__ == '__main__':
    feeder = upload_feeder_blazegraph()
    feeder.get_blazegraph_link()
    feeder.remove_all_feeders()
    feeder.upload_model_to_blazegraph()
    feeder.list_feeders()
    # feeder.insert_der_and_measurements()

