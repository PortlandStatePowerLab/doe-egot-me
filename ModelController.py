"""
model controller
"""
import ast
import csv

import pandas as pd
from gridappsd import GridAPPSD, goss, DifferenceBuilder
from gridappsd import topics as t
from gridappsd.simulation import Simulation
import time
# import datetime
# import json
# import csv
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
    mrid_name_lookup_table = []

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
        # TODO: Assign all DERS
        # TODO: Provide association table to ID Manager
        self.load_config_from_file()
        self.initialize_line_mrid()
        self.establish_mrid_name_lookup_table()
        self.connect_to_simulation()
        self.initialize_sim_start_time()
        self.initialize_sim_mrid()
        self.create_objects()
        self.initialize_all_der_s()
        mcOutputLog.set_log_name()
        # TODO: Connect to aggregator

    def load_config_from_file(self):
        with open(self.config_file_path) as f:
            config_string = f.read()
            self.config_parameters = ast.literal_eval(config_string)

    def connect_to_gridapps(self):
        self.gapps_session = GridAPPSD("('localhost', 61613)", username='system', password='manager')

    def initialize_sim_mrid(self):
        self.sim_mrid = self.sim_session.simulation_id
        print(self.sim_mrid)

    def initialize_line_mrid(self):
        self.line_mrid = self.config_parameters["power_system_config"]["Line_name"]

    def initialize_sim_start_time(self):
        self.sim_start_time = self.config_parameters["simulation_config"]["start_time"]
        print("Simulation start time is:")
        print(self.sim_start_time)

    def connect_to_simulation(self):
        self.sim_session = Simulation(self.gapps_session, self.config_parameters)

    def create_objects(self):
        global mcOutputLog
        mcOutputLog = MCOutputLog()
        global mcInputInterface
        mcInputInterface = MCInputInterface()
        global dersHistoricalDataInput
        dersHistoricalDataInput = DERSHistoricalDataInput()
        # TODO: This doesn't work, probably due to scope stuff. Do some research on it.
        # global edmMeasurementProcessor
        # edmMeasurementProcessor = EDMMeasurementProcessor(self.sim_mrid, self.gapps_session, self)
        # self.gapps_session.subscribe(t.simulation_output_topic(self.sim_mrid), edmMeasurementProcessor)
        # global edmTimekeeper
        # edmTimekeeper = EDMTimeKeeper(self.sim_mrid, self.gapps_session, self)
        # self.gapps_session.subscribe(t.simulation_log_topic(self.sim_mrid), edmTimekeeper)

    def initialize_all_der_s(self):
        #Comment out as required.
        dersHistoricalDataInput.initialize_der_s()

    def start_simulation(self):
        self.initialize_sim_start_time()
        self.sim_session.start_simulation()

    def establish_mrid_name_lookup_table(self):
        topic = "goss.gridappsd.process.request.data.powergridmodel"
        message = {
            "modelId": edmCore.get_line_mrid(),
            "requestType": "QUERY_OBJECT_MEASUREMENTS",
            "resultFormat": "JSON",
        }
        print(edmCore.get_line_mrid())
        object_meas = edmCore.gapps_session.get_response(topic, message)
        self.mrid_name_lookup_table = object_meas['data']

    def get_mrid_name_lookup_table(self):
        return self.mrid_name_lookup_table


class EDMTimeKeeper(object):

    def __init__(self, simulation_id, gapps_object, edmCore):
        self._gapps = gapps_object
        self._simulation_id = simulation_id
        self.sim_start_time = edmCore.get_sim_start_time()
        self.sim_current_time = self.sim_start_time
        self.previous_log_message = None
        self.edmCore = edmCore


    def on_message(self, sim, message):
        def end_program():
            mcOutputLog.close_out_logs()
            global end_program
            end_program = True

        def update_and_increment_timestep(log_message, self):
            if "incrementing to " in log_message:
                if log_message != self.previous_log_message:
                    print(log_message)
                    self.increment_sim_current_time()
                    # print("Start time: " + self.sim_start_time)
                    print("Current timestep: " + self.sim_current_time)
                    self.perform_all_on_timestep_updates()
                    self.previous_log_message = log_message

        log_message = message["logMessage"]
        process_status = message['processStatus']
        try:
            if process_status == 'COMPLETE' or process_status == 'CLOSED':
                end_program()
            else:
                update_and_increment_timestep(log_message, self)
        except KeyError as e:
            print(e)
            print("KeyError!")
            print(message)

    def increment_sim_current_time(self):
        current_int_time = int(self.sim_current_time)
        current_int_time += 1
        self.sim_current_time = str(current_int_time)

    def get_sim_current_time(self):
        return self.sim_current_time

    def perform_all_on_timestep_updates(self):
        print("Performing on-timestep updates:")
        self.edmCore.sim_current_time = self.sim_current_time
        mcInputInterface.update_all_der_s_status()
        mcInputInterface.update_all_der_em_status()
        mcOutputLog.update_logs()


class EDMMeasurementProcessor(object):

    def __init__(self, simulation_id, gapps_object, edmCore):
        self._gapps = gapps_object
        self._simulation_id = simulation_id
        self.measurement_timestamp = None
        self.current_measurements = None
        self.current_processed_grid_states = None
        self.run_once_flag = False
        self.mrid_name_lookup_table = []

    def on_message(self, headers, measurements):
        self.parse_message_into_current_measurements(measurements)

    def get_current_measurements(self):
        return self.current_measurements

    def parse_message_into_current_measurements(self, measurement_message):
        # print(measurement_message)
        self.current_measurements = measurement_message['message']['measurements']
        # print(self.current_measurements)
        self.measurement_timestamp = measurement_message['message']['timestamp']
        # print(self.measurement_timestamp)

        # if not self.run_once_flag:
        #     timestamped_message = {
        #         self.measurement_timestamp: list(self.current_measurements.items())
        #     }
        #     message_df = pd.DataFrame.from_dict(timestamped_message, orient='index', columns=self.current_measurements.keys())
        #     print(message_df)
        #     self.current_measurements = message_df

    def append_association_data(self):
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
    historical_data_file_path = r"C:\Users\stant\PycharmProjects\doe-egot-me\input.csv"
    input_file_name = None
    input_table = None


    def initialize_der_s(self):
        self.open_input_file()
        self.read_input_file()

    def get_input_request(self):
        self.update_der_em_input_request()
        return self.der_em_input_request

    def assign_der_s_to_der_em(self):
        pass

    def open_input_file(self):
        with open(self.historical_data_file_path) as csvfile:
            r = csv.DictReader(csvfile)
            x = []
            for row in r:
                row = dict(row)
                x.append(row)
        print("Historical data file opened")
        return x

    def read_input_file(self):
        self.input_table = self.open_input_file()


    def update_der_em_input_request(self):
        try:
            input_at_time_now = next(item for item in self.input_table if int(item['Time']) >= int(edmCore.sim_current_time) and int(item['Time']) < (int(edmCore.sim_current_time) + 1))
            print("Updating DER-EMs from historical data.")
            self.der_em_input_request = dict(input_at_time_now)
            self.der_em_input_request.pop('Time')
            print("Current Historical Input DER-EM Input request:")
            print(self.der_em_input_request)

        except StopIteration:
            print("End of input data.")
            return


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
    test_DER_1_mrid = '_B1C7AD50-5726-4442-BA61-B8FA87C8E947'
    test_DER_2_mrid = '_2750969C-CBD5-41F4-BDCE-19287FBDCA71'
    test_DER_3_mrid = '_1720E0C8-A0CA-41BF-84DE-9847A17EBE26'


    def update_all_der_em_status(self):
        self.test_der_em()

    def update_all_der_s_status(self):
        self.get_all_der_s_input_requests()


    def get_all_der_s_input_requests(self):
        self.current_unified_input_request = dersHistoricalDataInput.get_input_request()
        print("Current unified input request:")
        print(self.current_unified_input_request)

    def send_der_em_updates_to_edm(self):
        pass

    def test_der_em(self):
        input_topic = t.simulation_input_topic(edmCore.sim_mrid)
        for key in self.current_unified_input_request:
            my_diff_build = DifferenceBuilder(edmCore.sim_mrid)
            my_diff_build.add_difference(key, "PowerElectronicsConnection.p", int(self.current_unified_input_request[key]), 0)
            message = my_diff_build.get_message()
            print(message)
            edmCore.gapps_session.send(input_topic, message)



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


class MCOutputLog:
    def __init__(self):
        self.csv_file = None
        self.log_name = ''
        self.mrid_name_lookup_table = []
        self.header_mrids = []
        self.header_names = []
        self.csv_dict_writer = None
        self.timestamp_array = []
        self.current_measurement = None
        self.is_first_measurement = True

    def update_logs(self):
        self.current_measurement = edmMeasurementProcessor.get_current_measurements()
        if self.current_measurement:
            print("Updating logs...")
            if self.is_first_measurement == True:
                print("First measurement routines...")
                self.set_log_name()
                self.open_csv_file()
                self.mrid_name_lookup_table = edmCore.get_mrid_name_lookup_table()
                self.translate_header_names()
                self.open_csv_dict_writer()
                self.write_header()
                self.is_first_measurement = False
            self.write_row()
            self.timestamp_array.append(edmTimekeeper.sim_current_time)
            print("Current array time:")
            print(self.timestamp_array)
        else:
            #print("skipping")
            pass

    def open_csv_file(self):
        self.csv_file = open(self.log_name, 'w')

    def open_csv_dict_writer(self):
        # Note: the dict writer uses mrids for processing purposes
        self.csv_dict_writer = csv.DictWriter(self.csv_file, self.header_mrids)

    def close_out_logs(self):
        self.csv_file.close()
        self.append_timestamps()

    def translate_header_names(self):
        self.header_mrids = self.current_measurement.keys()
        for i in self.header_mrids:
            try:
                lookup_mrid = next(item for item in self.mrid_name_lookup_table if item['measid'] == i)
            except StopIteration:
                print(lookup_mrid)
            lookup_name = lookup_mrid['name']
            self.header_names.append(lookup_name)
            # print(self.header_names)
        self.header_mrids = dict(zip(list(self.header_mrids), self.header_names))

    def write_header(self):
        self.csv_dict_writer.writerow(self.header_mrids)

    def write_row(self):
        self.csv_dict_writer.writerow(self.current_measurement)

    def set_log_name(self):
        self.log_name = 'testlog.csv'

    def append_timestamps(self):
        csv_input = pd.read_csv(self.log_name)
        self.timestamp_array = pd.to_datetime(self.timestamp_array, unit='s')
        csv_input['Timestamp'] = self.timestamp_array
        move_column = csv_input.pop('Timestamp')
        csv_input.insert(0, 'Timestamp', move_column)
        csv_input.to_csv(self.log_name, index=False)

# ---------------------------------------------------------------------------------------------------------------------
# Function Definitions
# ---------------------------------------------------------------------------------------------------------------------
# Probably unnecessary, since everything can be put in classes. Delete later if unused. ~SJK

# def MC_instantiate_all_classes():
#     print("Instantiating classes:")
#     # example = Example()

def instantiate_callback_classes(simulation_id, gapps_object, edmCore):
    global edmMeasurementProcessor
    edmMeasurementProcessor = EDMMeasurementProcessor(simulation_id, gapps_object, edmCore)
    edmCore.gapps_session.subscribe(t.simulation_output_topic(edmCore.sim_mrid), edmMeasurementProcessor)
    global edmTimekeeper
    edmTimekeeper = EDMTimeKeeper(simulation_id, gapps_object, edmCore)
    edmCore.gapps_session.subscribe(t.simulation_log_topic(edmCore.sim_mrid), edmTimekeeper)


# --------------------------------------------------------------------------------------------------------------------
# Program Execution
# --------------------------------------------------------------------------------------------------------------------
def _main():
    global edmCore
    edmCore = EDMCore()  # EDMCore must be manually instantiated.
    edmCore.sim_start_up_process()
    edmCore.start_simulation()
    edmCore.initialize_sim_mrid()
    instantiate_callback_classes(edmCore.sim_mrid, edmCore.gapps_session, edmCore)

    global end_program
    while not end_program:
        time.sleep(0.1)

    if end_program:
        print('Ending program.')
        quit()


if __name__ == "__main__":
    _main()
