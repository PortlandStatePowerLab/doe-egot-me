'''
model controller
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
    config_file_path = None

    def get_sim_start_time(self):
        pass

    def get_sim_current_time(self):
        pass

    def get_line_mrid(self):
        pass

    def increment_sim_current_time(self):
        pass

    def sim_start_up_process(self):
        pass

    def load_config_from_file(self):
        pass

    def connect_to_gridapps(self):
        pass

    def initialize_sim_mrid(self):
        pass

    def connect_to_simulation(self):
        pass

    def create_callback_objects(self):
        pass

    def start_simulation(self):
        pass


class EDMTimeKeeper:
    sim_start_time = None
    sim_current_time = None

    def on_message(self):
        pass


class EDMMeasurementProcessor:
    measured_timestamp = None
    current_measurements = None
    current_processed_grid_states = None

    def on_message(self):
        pass

    def parse_message_into_current_measurements(self):
        pass

    def append_association_data(self):
        pass


class EDMOnClose:

    def force_quit(self):
        pass

    def on_message(self):
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

def MC_instantiate_all_classes():
    print("Instantiating classes:")
    # example = Example()

# --------------------------------------------------------------------------------------------------------------------
# Program Execution
# --------------------------------------------------------------------------------------------------------------------
