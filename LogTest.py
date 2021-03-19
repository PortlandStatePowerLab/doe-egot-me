'''

This is a test script that will either develop into or be replaced by the eventual 'Log API' as designed for the EGot
Modeling Environment (ME).

~Sean Keene, Portland State University, 2021
seakeene@pdx.edu
'''
from gridappsd import GridAPPSD, goss
from gridappsd import topics as t
from gridappsd.simulation import Simulation
from gridappsd.topics import simulation_input_topic, simulation_output_topic, simulation_log_topic
import time
import json
import pandas as pd
import csv

global simulation_id, end_program, flag, w
flag = 0

def callback(headers, message):
    global end_program, flag, w
    publish_to_topic = simulation_input_topic(simulation_id)
    if type(message) == str:
            message = json.loads(message)
    if 'message' not in message:
        if message['processStatus'] == 'COMPLETE' or \
           message['processStatus']=='CLOSED':
            print('The End')
            end_program = True
    else:
        print(message)
        if flag == 0:
            w = csv.DictWriter(f, message['message']['measurements'].keys())
            w.writeheader()
            flag = 1

        print(type(message))
        w.writerow(message['message']['measurements'])

def callback2(headers, message):
    global end_program
    publish_to_topic = simulation_log_topic(simulation_id)
    if type(message) == str:
            message = json.loads(message)
    print(message)

    if 'message' not in message:
        if message['processStatus'] == 'COMPLETE' or \
           message['processStatus']=='CLOSED':
            print('The End')
            end_program = True
    else:
        print(message)


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

#Playing around with simulations. See if I can get a 13 node, 120 second simulation running.

topic = t.REQUEST_SIMULATION

run_config_13 = {
    "power_system_config": {
        "GeographicalRegion_name": "_73C512BD-7249-4F50-50DA-D93849B89C43",
        "SubGeographicalRegion_name": "_ABEB635F-729D-24BF-B8A4-E2EF268D8B9E",
        "Line_name": "_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62"
    },
    "application_config": {
        "applications": []
    },
    "simulation_config": {
        "start_time": "1570041113",
        "duration": "21",
        "simulator" : "GridLAB-D",
        "timestep_frequency": "1000",
        "timestep_increment": "1000",
        "run_realtime": True,
        "simulation_name": "ieee123",
        "power_flow_solver_method": "NR",
        "model_creation_config":{
            "load_scaling_factor": "1",
            "schedule_name": "ieeezipload",
            "z_fraction": "0",
            "i_fraction": "1",
            "p_fraction": "0",
            "randomize_zipload_fractions": False,
            "use_houses": False
        }

    },
    # #Test Config is optional! This example is copied from the hackathon for syntax comparison
    # "test_config": {
    #     "events": [{
    #         "message": {
    #             "forward_differences": [
    #                 {
    #                     "object": "_6C1FDA90-1F4E-4716-BC90-1CCB59A6D5A9",
    #                     "attribute": "Switch.open",
    #                     "value": 1
    #                 }
    #             ],
    #             "reverse_differences": [
    #                 {
    #                     "object": "_6C1FDA90-1F4E-4716-BC90-1CCB59A6D5A9",
    #                     "attribute": "Switch.open",
    #                     "value": 0
    #                 }
    #             ]
    #         },
    #         "event_type": "ScheduledCommandEvent",
    #         "occuredDateTime": 1570041140,
    #         "stopDateTime": 1570041200
    #     }]
    # },
}

#Start the simulation....

gapps_sim = GridAPPSD()
simulation = Simulation(gapps_sim, run_config_13)
simulation.start_simulation()

simulation_id = simulation.simulation_id
print(simulation_id)

#Test the callback function
sim_output_topic = simulation_output_topic(simulation_id)
f = open('csvwritertest.csv', 'w')

gapps.subscribe(sim_output_topic, callback)
sim_log_topic = simulation_log_topic(simulation_id)
gapps.subscribe(sim_log_topic, callback2)

def _main():
    global end_program
    end_program = False
    print('test')
    while not end_program:
        time.sleep(0.1)
    if end_program:
        f.close()
        print('bye')

if __name__ == "__main__":
    _main()