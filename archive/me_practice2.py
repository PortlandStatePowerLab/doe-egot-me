from gridappsd import GridAPPSD,DifferenceBuilder
from gridappsd import topics as t
from gridappsd.simulation import Simulation
import ast
from pathlib import Path
import os
import pprint
import pandas as pd
import csv

dire=str(Path().absolute())

with open(dire+"/Configuration/config_midrar.txt") as f:
    config_string = f.read()
    config_parameters = ast.literal_eval(config_string)

os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
os.environ['GRIDAPPSD_PORT'] = '61613'

gapps_session = GridAPPSD()
assert gapps_session.connected


get_line_mrid = "F234F944-6C06-4D13-8E87-3532CDB095FA"
topic = "goss.gridappsd.process.request.data.powergridmodel"
message = {"modelId": get_line_mrid,"requestType": "QUERY_OBJECT_MEASUREMENTS","resultFormat": "JSON",}
object_meas = gapps_session.get_response(topic, message)
pprint.pprint(object_meas)
# mrid_name_lookup_table = object_meas['data']
# config_api_topic = 'goss.gridappsd.process.request.config'
# message = {'configurationType': 'CIM Dictionary','parameters': {'model_id': get_line_mrid}}
# cim_dict = gapps_session.get_response(config_api_topic, message, timeout=20)
# measdict = cim_dict['data']['feeders'][0]['measurements']
# cim_measurement_dict = measdict
# pprint.pprint(measdict)
