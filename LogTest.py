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
import datetime
import json
import pandas as pd
import csv

global simulation_id, end_program, flag, w, SIMULATION_TIME, log_timestamps
end_program=False
log_timestamps = []
flag = 0

def callback(headers, message):
    global end_program, flag, w, log_timestamps
    log_timestamp = []
    publish_to_topic = simulation_input_topic(simulation_id)
    if type(message) == str:
            message = json.loads(message)
    if 'message' not in message:
        if message['processStatus'] == 'COMPLETE' or \
           message['processStatus']=='CLOSED':
            print('The End')
            end_program = True
    else:
        #Uncomment for troubleshooting
        print(message)

        '''
        Only runs the first output query. Grabs the keys from the message, looks them up for their real names, and
        writes the header with the real names while still using the mrids as headers for dictwriter purposes.
        '''
        if flag == 0:
            header_mrids = message['message']['measurements'].keys()
            header_names = []
            print(header_mrids)
            for i in header_mrids:
                lookup_mrid = next(item for item in meas_object_list if item['measid'] == i)
                lookup_name = lookup_mrid['name']
                header_names.append(lookup_name)
            w = csv.DictWriter(f, header_mrids)
            print(header_names)
            header_names_dict = dict(zip(list(header_mrids),header_names))
            w.writerow(header_names_dict)
            flag = 1
        else:
            pass

        print(type(message))
        w.writerow(message['message']['measurements'])
        log_timestamps.append(SIMULATION_TIME)

def callback2(headers, message):
    global end_program, SIMULATION_TIME, log_timestamps
    publish_to_topic = simulation_log_topic(simulation_id)
    if type(message) == str:
            message = json.loads(message)
    print(message)
    SIMULATION_TIME = message["timestamp"]
    print(SIMULATION_TIME)
    if 'message' not in message:
        if message['processStatus'] == 'COMPLETE' or \
           message['processStatus']=='CLOSED':
            print('Adding timestamps to logs...')
            f.close()
            #Use pandas to append timestamps
            csv_input = pd.read_csv('csvwritertest.csv')
            print(csv_input)
            print(log_timestamps)
            log_timestamps = pd.to_datetime(log_timestamps, unit='ms')
            csv_input['Timecode'] = log_timestamps
            movecolumn = csv_input.pop("Timecode")
            csv_input.insert(0, "Timecode", movecolumn)
            csv_input.to_csv('csvwritertest.csv', index=False)
            print("Ending Simulation...")
            end_program = True
            quit()
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


# #Playing around with queries. This gets us object IDs from the 13 node model.
# topic = "goss.gridappsd.process.request.data.powergridmodel"
# message = {
#     "requestType": "QUERY_OBJECT_IDS",
#     "resultFormat": "JSON",
#     "modelId": model_mrid
# }
#
# object_dict = gapps.get_response(topic, message)
# print('Object dictionary: \n')
# print(object_dict)
# print('\n')
# object_mrid_list = object_dict['data']['objectIds']
# print('Object List: \n')
# print(object_mrid_list)

#Initialize lookup list for measurement mrid names
topic = "goss.gridappsd.process.request.data.powergridmodel"
message = {
        "modelId": model_mrid,
        "requestType": "QUERY_OBJECT_MEASUREMENTS",
        "resultFormat": "JSON",
}

object_meas = gapps.get_response(topic, message)
meas_object_list = object_meas['data']

#Example for how to grab a name given a measurement id
#testvar = next(item for item in meas_object_list if item['measid'] == '_08175e8f-b762-4c9b-92c4-07f369f69bd4')
#print(testvar)
#name = testvar['name']
#print(name)

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
    print('test')
    while not end_program:
        time.sleep(0.1)
    if end_program:
        f.close()
        print('bye')
        quit()

if __name__ == "__main__":
    _main()


