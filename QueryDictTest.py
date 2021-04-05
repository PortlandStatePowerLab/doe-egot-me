'''
This script is a simple functional test of multiple queries available in the gridappsd library as well as
a direct topic message
'''


from gridappsd import GridAPPSD, goss
from gridappsd import topics as t
from gridappsd.simulation import Simulation
from gridappsd.topics import simulation_input_topic, simulation_output_topic, simulation_log_topic
import time
import json
import pandas as pd
import csv

gapps = GridAPPSD("('localhost', 61613)", username='system', password='manager')
#model_names = gapps.query_model_names()
#print(model_names)

#model_check = gapps.query_model_info()
#print(model_check)


model_mrid = '_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62'




#full_object_list = gapps.query_object_types()
#print(full_object_list)
object_list = gapps.query_object_types(model_mrid)
print("Object List")
print(object_list)

object_type = 'ConnectivityNode'


object_search = gapps.query_object('_08175e8f-b762-4c9b-92c4-07f369f69bd4')
print("Query Object")
print(object_search)


x=gapps.query_object_dictionary(model_mrid, '_08175e8f-b762-4c9b-92c4-07f369f69bd4')
print("Object Dictionary")
print(x)

y = gapps.query_object('_08175e8f-b762-4c9b-92c4-07f369f69bd4', model_mrid)
print("Measurement Query")
print(y)

topic = "goss.gridappsd.process.request.data.powergridmodel"
message = {
        "modelId": model_mrid,
        "requestType": "QUERY_OBJECT_MEASUREMENTS",
        "resultFormat": "JSON",
}

object_meas = gapps.get_response(topic, message)

object_meas = object_meas['data']

testvar = next(item for item in object_meas if item['measid'] == '_08175e8f-b762-4c9b-92c4-07f369f69bd4')
print(testvar)
name = testvar['name']
print(name)