'''

This is a test script that will either develop into or be replaced by the eventual 'Log API' as designed for the EGot
Modeling Environment (ME).

~Sean Keene, Portland State University, 2021
seakeene@pdx.edu
'''
from gridappsd import GridAPPSD, goss
from gridappsd import topics as t
from gridappsd.topics import simulation_input_topic, simulation_output_topic

#Connect to GridAPPS
gapps = GridAPPSD("('localhost', 61613)", username='system', password='manager')

#Define topic and message for id query
topic = t.REQUEST_POWERGRID_DATA
message = {
    "requestType": "QUERY_MODEL_NAMES",
    "resultFormat": "JSON"
}

#Query the model names. We know the mrid already, but this gives us our simulation id as well.
x = gapps.get_response(topic, message)
simulation_id = x["id"]
model_mrid = "_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62" #for 13 node feeder


#Playing around with queries. This gets us object IDs from the 13 node model.
topic = "goss.gridappsd.process.request.data.powergridmodel"
message = {
    "requestType": "QUERY_OBJECT_IDS",
    "resultFormat": "JSON",
    "modelId": model_mrid
}

object_dict = gapps.get_response(topic, message)
print('Object dictionary: \n')
print(object_dict)
print('\n')
object_mrid_list = object_dict['data']['objectIds']
print('Object List: \n')
print(object_mrid_list)