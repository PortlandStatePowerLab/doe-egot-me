# Upload no loads psu feeder model
import os
import cimhub.api as cimhub
from pprint import pprint as pp
from gridappsd import GridAPPSD
from gridappsd import topics as t
import cimhub.CIMHubConfig as CIMHubConfig

main_dir = os.getcwd()
cfg_json = f'{main_dir}/cimhub_config_files/cimhubdocker.json'
dss_name = 'Master'

cimhub.clear_db (cfg_json)
os.system(f'curl -D- -H "Content-Type: application/xml" --upload-file {main_dir}/dss_no_loads/{dss_name}.xml -X POST {CIMHubConfig.blazegraph_url}')
cimhub.list_feeders()

# query loads type:
os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
os.environ['GRIDAPPSD_PORT'] = '61613'
# Connect to GridAPPS-D Platform
gapps_session = GridAPPSD()
