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

current_dir = path().absolute()
me_dir = '/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/DERScripts/'

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
    # The following requestType and objectType are related to ONLY mRIDs for a specific set of feeders or set of equipment.
    # The message will need to be modified. Look at this link https://gridappsd-training.readthedocs.io/en/develop/api_usage/3.3-Using-the-PowerGrid-Models-API.html#CIM-Objects-Supported-by-PowerGrid-Models-API
    # Query the list of all model name mRIDs (Not really useful since only the psu model is in there!)
    modelNames = {
    "requestType": "QUERY_MODEL_NAMES",
    "resultFormat": "JSON"
    }
    
    # The following message returns the objectType mRIDs.
    objectType_mRIDs = {
    "requestType": "QUERY_OBJECT_IDS",
    "modelId": "_597ADC83-1B79-4560-83DB-DFBED03732D8",
    "objectType": "EnergyConsumer",
    "resultFormat": "JSON"
    }

    # Returns all specifics of a feeder or a SET of equipments
    objectInfo = {
    "requestType": "QUERY_OBJECT_DICT",
    "modelId": "_859AC45B-99CC-4250-8FE6-23CF2532ECFF",
    "objectType": "EnergyConsumer",
    "resultFormat": "JSON"
    }
    
    # Returns the detailed mRIDs for each feeder within the Blazegraph
    Model_detailed_info = {
    "requestType": "QUERY_MODEL_INFO",
    "resultFormat": "JSON"
    }
    # Returns the types of CIM classes. It is important to create the EGoT13_der_psu.txt
    CIMClassesTypes = {
    "requestType": "QUERY_OBJECT_TYPES",
    "resultFormat": "JSON"
    }

    # The following returns a specific object (objectID) attributes
    CIMObjectAttr = {
    "requestType": "QUERY_OBJECT",
    "resultFormat": "JSON",
    "modelId": "_597ADC83-1B79-4560-83DB-DFBED03732D8",
    "objectId": "_01300AA7-29D6-4DD6-B729-58AEDC1EA92F"
    }

    return objectInfo

def wr_csv(data, me_dir):
    df = pd.DataFrame(data)
    df.to_csv(f"{me_dir}EGoT13_orig_der_psu.txt",header=False, index=False)


def config_file_to_remove_existing_ders(me_dir):
    data = []
    tree = et.parse("../dss/Master.xml")
    root = tree.getroot()
    energy_consumer_found = False
    d = {"{http://iec.ch/TC57/CIM100#}Location": ['mRID','name']}
    for child in root.iter():
        term = child.tag.split('}')[1]
        if term == 'EnergyConsumer':
             energy_consumer_found = True
        if energy_consumer_found and ((term == 'EnergyConsumer') or (term == 'Terminal') or (term == 'Location')):
            mrid_tag = '{http://iec.ch/TC57/CIM100#}IdentifiedObject.mRID'
            name_tag = '{http://iec.ch/TC57/CIM100#}IdentifiedObject.name'
            x = child.find(mrid_tag)
            y = child.find(name_tag)
            data.append((child.tag.split('}')[1],y.text,x.text))

    wr_csv(data, me_dir)
    
def main(me_dir):
    gapps_session = connect_to_GridAPPSD()
    message = request_types()
    # Need one of the above queries? Return its variable in request_types func and uncomment the following line.
    # query(gapps_session, message)
    config_file_to_remove_existing_ders(me_dir)

    
main(me_dir)