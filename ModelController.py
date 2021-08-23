"""
model controller
"""
import ast

import pandas as pd
from gridappsd import GridAPPSD  # , goss, DifferenceBuilder
from gridappsd import topics as t
from gridappsd.simulation import Simulation
import time
# import datetime
# import json
# import pandas as pd
# import csv
global end_program
end_program = False



# -------------------------------------------------------------------------------------------------------------------
#   Class Definitions
# --------------------------------------------------------------------------------------------------------------------
class EDMCore:
    gapps_session = None
    sim_session = None
    sim_start_time = None
    sim_current_time = None
    sim_mrid = None
    line_mrid = None
    config_parameters = None
    config_file_path = r"C:\Users\stant\PycharmProjects\doe-egot-me\Config.txt"

    def get_sim_start_time(self):
        return self.sim_start_time

    def get_sim_current_time(self):
        return self.sim_current_time

    def get_line_mrid(self):
        return self.line_mrid

    def increment_sim_current_time(self):
        int_time = int(self.sim_current_time)
        int_time += 1
        self.sim_current_time = int_time

    def sim_start_up_process(self):
        self.connect_to_gridapps()
        self.initialize_sim_mrid()
        # TODO: Create Assignment Lookup Table
        # TODO: Assign all DERS
        # TODO: Provide association table to ID Manager
        self.load_config_from_file()
        self.initialize_sim_start_time()
        self.connect_to_simulation()
        # TODO: Create Callback objects
        # TODO: Set log name
        # TODO: Open log .csv file
        # TODO: Connect to aggregator
        self.start_simulation()

    def load_config_from_file(self):
        with open(self.config_file_path) as f:
            config_string = f.read()
            self.config_parameters = ast.literal_eval(config_string)

    def connect_to_gridapps(self):
        self.gapps_session = GridAPPSD("('localhost', 61613)", username='system', password='manager')

    def initialize_sim_mrid(self):
        topic = t.REQUEST_POWERGRID_DATA
        message = {
            "requestType": "QUERY_MODEL_NAMES",
            "resultFormat": "JSON"
        }
        x = self.gapps_session.get_response(topic, message)
        self.sim_mrid = x["id"]

    def initialize_line_mrid(self):
        self.line_mrid = self.config_parameters["power_system_config"]["Line_name"]

    def initialize_sim_start_time(self):
        self.sim_start_time = self.config_parameters["simulation_config"]["start_time"]

    def connect_to_simulation(self):
        self.sim_session = Simulation(self.gapps_session, self.config_parameters)

    def create_callback_objects(self):
        pass

    def start_simulation(self):
        self.sim_session.start_simulation()


class EDMTimeKeeper(object):
    sim_start_time = None
    sim_current_time = None

    def __init__(self, simulation_id, gapps_object, edmCore):
        self._gapps = gapps_object
        self._simulation_id = simulation_id
        self.sim_start_time = edmCore.get_sim_start_time()
        self.sim_current_time = self.sim_start_time


    def on_message(self, sim, timestep):
        self.increment_sim_current_time()
        print("Current timestep: " + self.sim_current_time)
        self.perform_all_on_timestep_updates()

    def increment_sim_current_time(self):
        current_int_time = int(self.sim_current_time)
        current_int_time += 1
        self.sim_current_time = str(current_int_time)

    def get_sim_current_time(self):
        return self.sim_current_time

    def perform_all_on_timestep_updates(self):
        print("Performing on-timestep updates:")
        pass



class EDMMeasurementProcessor(object):

    def __init__(self, simulation_id, gapps_object, edmCore):
        self._gapps = gapps_object
        self._simulation_id = simulation_id
        self.measurement_timestamp = None
        self.current_measurements = None
        self.current_processed_grid_states = None
        self.run_once_flag = False

    def on_message(self, sim, timestamp, measurements):
        self.current_measurements = measurements
        self.measurement_timestamp = timestamp
        # print(self.current_measurements)
        self.parse_message_into_current_measurements()

    def parse_message_into_current_measurements(self):

        if self.run_once_flag == False:
            timestamped_message = {
                "Timestamp": self.measurement_timestamp,
                "Measurements": self.current_measurements
            }
            message_df = pd.DataFrame(timestamped_message)
            print(message_df)


    def append_association_data(self):
        pass


class EDMOnClose:

    def force_quit(self):
        pass

    def on_message(self, sim):
        pass


class RWHDERS:
    current_input_request = None
    current_der_states = None

    def assign_DER_S_to_DER_EM(self):
        pass

    def gather_DER_EM_identification_data(self):
        pass

    def update_wh_states_from_emulator(self):
        pass

    def update_DER_EM_input_request(self):
        pass


class DERSHistoricalDataInput:
    der_em_input_request = None
    historical_data_file_path = None
    input_file = None
    input_table = None

    def get_input_request(self):
        pass

    def assign_der_s_to_der_em(self):
        pass

    def open_input_file(self):
        pass

    def read_input_file(self):
        pass

    def update_der_em_input_request(self):
        pass


class DERIdentificationManager:
    association_lookup_table = None

    def get_meas_name(self):
        pass

    def get_der_em_mrid(self):
        pass

    def get_der_em_service_location(self):
        pass

    def get_association_table_from_assignment_handler(self):
        pass


class DERAssignmentHandler:
    der_em_assignment_list = None
    assignment_lookup_table = None
    location_data = None
    ders_in_use = None

    def get_assignment_lookup_table(self):
        pass

    def create_assignment_lookup_table(self):
        pass

    def assign_all_ders(self):
        pass


class MCInputInterface:
    current_unified_input_request = None
    active_der_s_list = None

    def update_all_der_em_status(self):
        pass

    def update_all_der_s_status(self):
        pass

    def get_all_der_s_input_requests(self):
        pass

    def send_der_em_updates_to_edm(self):
        pass


class GOSensor:
    current_grid_states = None
    current_sensor_states = None
    service_request_decision = None

    def get_service_request_decision(self):
        pass

    def get_sensor_status(self):
        pass

    def read_sensors(self):
        pass

    def make_service_request_decision(self):
        pass


class GOOutputInterface:
    connection_status = None
    current_service_request = None
    service_request_status = None

    def ping_aggregator(self):
        pass

    def connect_to_aggregator(self):
        pass

    def disconnect_from_aggregator(self):
        pass

    def update_service_request_decision(self):
        pass

    def create_service_request_decision(self):
        pass

    def send_service_request(self):
        pass

# ---------------------------------------------------------------------------------------------------------------------
# Function Definitions
# ---------------------------------------------------------------------------------------------------------------------
# Probably unnecessary, since everything can be put in classes. Delete later if unused. ~SJK

# def MC_instantiate_all_classes():
#     print("Instantiating classes:")
#     # example = Example()

def initialize_callback_functions(edmCore):
    """
    TODO: Remove. This is used for callback functions, which will be replaced by callback classes as soon as I can
    get that working.
    """
    edmCore.sim_session.add_ontimestep_callback(ontimestep)
    edmCore.sim_session.add_onmesurement_callback(onmeas)
    edmCore.sim_session.add_oncomplete_callback(onclose)

def ontimestep(sim, timestep):
    edmTimekeeper.on_message(sim, timestep)

def onmeas(sim, timestamp, measurements):
    edmMeasurementProcessor.on_message(sim, timestamp, measurements)

def onclose(sim):
    global end_program
    print("test onclose")
    end_program = True

def init_temporary_callback_method(simulation_id, gapps_object, edmCore):
    global edmTimekeeper
    edmTimekeeper = EDMTimeKeeper(simulation_id, gapps_object, edmCore)
    edmCore.gapps_session.subscribe(t.simulation_log_topic(edmCore.sim_mrid), edmTimekeeper)

    global edmMeasurementProcessor
    edmMeasurementProcessor = EDMMeasurementProcessor(simulation_id, gapps_object, edmCore)
    edmCore.gapps_session.subscribe(t.simulation_output_topic(edmCore.sim_mrid), edmMeasurementProcessor)

    global edmOnClose
    edmOnClose = EDMOnClose()

# --------------------------------------------------------------------------------------------------------------------
# Program Execution
# --------------------------------------------------------------------------------------------------------------------
def _main():

    edmCore = EDMCore()  # EDMCore must be manually instantiated.




    edmCore.sim_start_up_process()

    # gapps = GridAPPSD(edmCore.sim_mrid)
    # edmMeasProc = EDMMeasurementProcessor(edmCore.sim_mrid, gapps)
    # gapps.subscribe(t.simulation_output_topic(edmCore.sim_mrid), edmMeasProc)

    # initialize_callback_functions(edmCore)
    init_temporary_callback_method(edmCore.sim_mrid, edmCore.gapps_session, edmCore)
    global end_program
    while not end_program:
        time.sleep(0.1)

    if end_program:
        print('Ending program.')
        quit()


if __name__ == "__main__":
    _main()
