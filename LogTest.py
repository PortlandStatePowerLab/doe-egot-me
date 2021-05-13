'''

This is a test script that will either develop into or be replaced by the eventual 'Log API' as designed for the EGot
Modeling Environment (ME).

~Sean Keene, Portland State University, 2021
seakeene@pdx.edu
'''
from gridappsd import GridAPPSD, goss, DifferenceBuilder
from gridappsd import topics as t
from gridappsd.simulation import Simulation
from gridappsd.topics import simulation_input_topic, simulation_output_topic, simulation_log_topic
import time
import datetime
import json
import pandas as pd
import csv

global simulation_id, end_program, SIMULATION_TIME, flag, w, log_timestamps, start_time, simulation_time, flag, sw_mrid
start_time = 1570041113
simulation_time = 0
SIMULATION_TIME = 0
end_program=False
log_timestamps = []
flag = 0

# def callback(headers, message):
#     global end_program, flag, w, log_timestamps
#     log_timestamp = []
#     publish_to_topic = simulation_input_topic(simulation_id)
#     if type(message) == str:
#             message = json.loads(message)
#     if 'message' not in message:
#         if message['processStatus'] == 'COMPLETE' or \
#            message['processStatus']=='CLOSED':
#             print('Ending Program...')
#             end_program = True
#     else:
#         #Uncomment for troubleshooting
#         #print(message)
#         SIMULATION_TIME = message["message"]["timestamp"]
#         print(SIMULATION_TIME)
#         '''
#         Only runs the first output query. Grabs the keys from the message, looks them up for their real names, and
#         writes the header with the real names while still using the mrids as headers for dictwriter purposes.
#         '''
#         if flag == 0:
#             header_mrids = message.keys()
#             header_names = []
#             #print(header_mrids)
#             for i in header_mrids:
#                 lookup_mrid = next(item for item in meas_object_list if item['measid'] == i)
#                 lookup_name = lookup_mrid['name']
#                 header_names.append(lookup_name)
#             w = csv.DictWriter(f, header_mrids)
#             print(header_names)
#             header_names_dict = dict(zip(list(header_mrids),header_names))
#             w.writerow(header_names_dict)
#             flag = 1
#         else:
#             pass
#
#         #print(type(message))
#         w.writerow(message['message']['measurements'])
#         log_timestamps.append(SIMULATION_TIME)

# def callback2(headers, message):
#     global end_program, SIMULATION_TIME, log_timestamps
#     publish_to_topic = simulation_log_topic(simulation_id)
#     if type(message) == str:
#             message = json.loads(message)
#     #print(message)
#
#     if 'message' not in message:
#         if message['processStatus'] == 'COMPLETE' or \
#            message['processStatus']=='CLOSED':
#
#     else:
#         print('test')



def onmeasurement(sim, timestamp, measurements):
    global end_program, flag, w, log_timestamps
    print('Measurement Test')
    #print(sim)
    #print(timestamp)
    print(measurements)
    SIMULATION_TIME = timestamp
    print(SIMULATION_TIME)
    '''
    Only runs the first output query. Grabs the keys from the message, looks them up for their real names, and
    writes the header with the real names while still using the mrids as headers for dictwriter purposes.
    '''
    if flag == 0:
        header_mrids = measurements.keys()
        header_names = []
        print(header_mrids)
        for i in header_mrids:
            lookup_mrid = next(item for item in meas_object_list if item['measid'] == i)
            lookup_name = lookup_mrid['name']
            header_names.append(lookup_name)
        w = csv.DictWriter(f, header_mrids)
        print(header_names)
        header_names_dict = dict(zip(list(header_mrids), header_names))
        w.writerow(header_names_dict)
        flag = 1
    else:
        pass

    # print(type(message))
    w.writerow(measurements)
    log_timestamps.append(SIMULATION_TIME)



def ontimestep(sim, timestep):
    '''
    Performs these actions once every simulation timestep.
    Note: the timestep occurs simultaneously with the measurement message. This means that at any given measurement,
    this start time will increment to simulation_time+1, but the associate measurement will still be at simulation_time
    '''

    global simulation_time
    print("Before:")
    print(simulation_time)
    print("After:")
    simulation_time += 1
    print(simulation_time)
    try:
        input_at_time_now = next(item for item in table_from_csvin if int(item['Time']) >= simulation_time and int(item['Time']) < simulation_time+1)
        operate_switch(int(input_at_time_now['Switch']))
    except StopIteration:
        print("End of input data.")
        return


def onstart(sim):
    global start_time, simulation_time, input_topic, table_from_csvin
    print("Start time:")
    print(start_time)
    simulation_time = start_time
    table_from_csvin = process_input_csv('input.csv')

def oncomplete(sim):
    global end_program, log_timestamps
    print("Simulation complete.")
    print('Adding timestamps to logs...')
    f.close()
    # Use pandas to append timestamps
    csv_input = pd.read_csv('csvwritertest.csv')
    # print(csv_input)
    # print(log_timestamps)
    log_timestamps = pd.to_datetime(log_timestamps, unit='s')
    csv_input['Timecode'] = log_timestamps
    movecolumn = csv_input.pop("Timecode")
    csv_input.insert(0, "Timecode", movecolumn)
    csv_input.to_csv('csvwritertest.csv', index=False)
    print("Ending Simulation...")
    end_program = True
    quit()


def operate_switch(position):
        global input_topic, db1, db2, simulation_id, sw_mrid
        if position == 1:
            print('Closing Switch:')
            print(simulation_id)
            # Create the DifferenceBuilder to automate message construction.
            db1 = DifferenceBuilder(simulation_id)
            # Generate the proper message to open the switch.
            db1.add_difference(sw_mrid, "Switch.open", 0, 1)
            switch_message1 = db1.get_message()
            print(switch_message1)
            # Send message to the input topic (opened in onstart())
            switch_message = json.dumps(switch_message1)
            gapps.send(input_topic, switch_message)

        elif position == 0:
            print('Opening Switch:')
            # Create the DifferenceBuilder to automate message construction.
            db2 = DifferenceBuilder(simulation_id)
            # Generate the proper message to open the switch.
            db2.add_difference(sw_mrid, "Switch.open", 1, 0)
            switch_message2 = db2.get_message()
            print(switch_message2)
            # Send message to the input topic (opened in onstart())
            switch_message2 = json.dumps(switch_message2)
            gapps.send(input_topic, switch_message2)
        else:
            print('error')



def process_input_csv(inputfile):
    with open(inputfile) as csvfile:
        r = csv.DictReader(csvfile)
        x = []
        for row in r:
            x.append(row)
    return x

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

#Get switch MRIDs
message = {
    "modelId": model_mrid,
    "requestType": "QUERY_OBJECT_DICT",
    "resultFormat": "JSON",
    "objectType": "LoadBreakSwitch"
}

response_obj = gapps.get_response(t.REQUEST_POWERGRID_DATA, message)
switch_dict = response_obj["data"]
print(switch_dict)

# Filter to get mRID for switch SW2:
for index in switch_dict:
    if index["IdentifiedObject.name"] == '671692':
        sw_mrid = index["IdentifiedObject.mRID"]
        print(sw_mrid)
        #_517413CB-6977-46FA-8911-C82332E42884 for 671692

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
        "start_time": str(start_time),
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
}

#Start the simulation....

gapps_sim = GridAPPSD()
simulation = Simulation(gapps_sim, run_config_13)
simulation.add_onstart_callback(onstart)
simulation.add_ontimestep_callback(ontimestep)
simulation.add_onmesurement_callback(onmeasurement)
simulation.add_oncomplete_callback(oncomplete)
simulation.start_simulation()
simulation_id = simulation.simulation_id
input_topic = simulation_input_topic(simulation_id)

print("Sim ID:")
print(simulation_id)

#Test the callback function
# sim_output_topic = simulation_output_topic(simulation_id)
f = open('csvwritertest.csv', 'w')

# gapps.subscribe(sim_output_topic, callback)
# sim_log_topic = simulation_log_topic(simulation_id)
#gapps.subscribe(sim_log_topic, callback2)





def _main():
    global end_program, SIMULATION_TIME
    print('test')
    while not end_program:
        time.sleep(0.1)

    if end_program:
        f.close()
        print('bye')
        quit()

if __name__ == "__main__":
    _main()


