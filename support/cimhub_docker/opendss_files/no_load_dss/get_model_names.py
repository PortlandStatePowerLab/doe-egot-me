import os
import csv
import time
import json
import shutil
import xmltodict
import subprocess
import pandas as pd
import cimhub.api as cimhub
from pprint import pprint as pp
from pathlib import Path as path
from gridappsd import topics as t
import xml.etree.ElementTree as et
import xml.dom.minidom as dom_mini
from datetime import datetime as dt
import cimhub.CIMHubConfig as CIMHubConfig
from gridappsd.simulation import Simulation
from gridappsd import GridAPPSD, DifferenceBuilder

def upload_psu_model():
    os.system(f'curl -D- -H "Content-Type: application/xml" --upload-file Master.xml -X POST $DB_URL')

def connect_to_GridAPPSD():
    os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
    os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
    os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
    os.environ['GRIDAPPSD_PORT'] = '61613'

    # Connect to GridAPPS-D Platform
    gapps_session = GridAPPSD()
    return gapps_session

def query(gapps_session, message):
    topic = t.REQUEST_POWERGRID_DATA
    return gapps_session.get_response(topic, message)

def request_types():
    message = {
    "requestType": "QUERY_MODEL_INFO",
    "resultFormat": "JSON"
    }
    return message


def get_mrids(query_resp):
    mrids = {}
    for i in range(len(query_resp['data']['models'])):
        if query_resp['data']['models'][i]['modelName'].startswith('psu_'):
            mrids = {
                'line_name':query_resp['data']['models'][i]['modelId'],
                'geo_rgn':query_resp['data']['models'][i]['regionId'],
                'sub_rgn':query_resp['data']['models'][i]['subRegionId'],
                'simulation_name':query_resp['data']['models'][i]['modelName']
            }
    return mrids

def main():
    upload_psu_model()
    gapps_session = connect_to_GridAPPSD()
    message = request_types()
    query_resp = query(gapps_session,message)
    mrid = get_mrids(query_resp)
main()