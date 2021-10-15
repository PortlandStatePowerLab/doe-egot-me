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
import xml.etree.ElementTree as ET

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
        derAssignmentHandler.create_assignment_lookup_table()
        derAssignmentHandler.assign_all_ders()
        derIdentificationManager.get_association_table_from_assignment_handler()
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
        global derAssignmentHandler
        derAssignmentHandler = DERAssignmentHandler()
        global derIdentificationManager
        derIdentificationManager = DERIdentificationManager()
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
    der_em_input_request = []
    historical_data_file_path = r"C:\Users\stant\PycharmProjects\doe-egot-me\input2.csv"
    input_file_name = None
    input_table = None
    list_of_ders = []
    location_lookup_dictionary = {}


    def initialize_der_s(self):
        self.read_input_file()

    def get_input_request(self):
        self.update_der_em_input_request()
        return self.der_em_input_request

    def assign_der_s_to_der_em(self):
        for i in self.list_of_ders:
            der_being_assigned = {}
            der_being_assigned[i] = self.input_table[0][(self.location_lookup_dictionary[i])]
            der_being_assigned[i] = derAssignmentHandler.get_mRID_for_der_on_bus(der_being_assigned[i])
            assigned_der = dict([(value, key) for value, key in der_being_assigned.items()])
            derAssignmentHandler.association_table.append(assigned_der)

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
        print("Retrieving locational data:")
        first_row = next(item for item in self.input_table)
        first_row = dict(first_row)
        first_row.pop('Time')
        print("First row:")
        print(first_row)
        log_der_keys = list(first_row.keys())
        print(log_der_keys)
        iterator_index = 0
        for i in range(len(log_der_keys)):
            if i%2 == 0:
                der_name =log_der_keys[i]
            else:
                der_loc = log_der_keys[i]
                self.location_lookup_dictionary[der_name] = der_loc
                print("Current dict:")
                print(self.location_lookup_dictionary)
        self.list_of_ders = list(self.location_lookup_dictionary.keys())
        print("List of DERS:")
        print(self.list_of_ders)


    def update_der_em_input_request(self):

        try:
            input_at_time_now = next(item for item in self.input_table if int(item['Time']) >= int(edmCore.sim_current_time) and int(item['Time']) < (int(edmCore.sim_current_time) + 1))
            print("Updating DER-EMs from historical data.")
            print(input_at_time_now)
            input_at_time_now = dict(input_at_time_now)
            input_at_time_now.pop('Time')
            for i in self.list_of_ders:
                # print(i)
                self.der_em_input_request.append({i:input_at_time_now[i]})
                # print(self.der_em_input_request)
            # print("Current Historical Input DER-EM Input request:")
            # print(self.der_em_input_request)

        except StopIteration:
            print("End of input data.")
            return


class DERIdentificationManager:
    association_lookup_table = None

    def get_meas_name(self, mrid):
        pass

    def get_der_em_mrid(self, name):
        print(self.association_lookup_table)
        x = next(d for i,d in enumerate (self.association_lookup_table) if name in d)
        print('TEST')
        print(x)
        return x[name]

    def get_der_em_service_location(self):
        pass

    def get_association_table_from_assignment_handler(self):
        self.association_lookup_table = derAssignmentHandler.association_table


class DERAssignmentHandler:
    der_em_assignment_list = None
    assignment_lookup_table = None
    assignment_table = None
    association_table = []
    location_data = None
    ders_in_use = None
    der_em_mrid_per_bus_query_message = """
    # Storage - DistStorage (Simplified to output name, bus, and mRID)
    PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX c:  <http://iec.ch/TC57/CIM100#>
    SELECT ?name ?bus ?id (group_concat(distinct ?phs;separator="\\n") as ?phases) WHERE {
     ?s r:type c:BatteryUnit.
     ?s c:IdentifiedObject.name ?name.
     ?pec c:PowerElectronicsConnection.PowerElectronicsUnit ?s.
    VALUES ?fdrid {"_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62"}  # 13 bus
     OPTIONAL {?pecp c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?pec.
     ?pecp c:PowerElectronicsConnectionPhase.phase ?phsraw.
       bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) }
     bind(strafter(str(?s),"#_") as ?id).
     ?t c:Terminal.ConductingEquipment ?pec.
     ?t c:Terminal.ConnectivityNode ?cn.
     ?cn c:IdentifiedObject.name ?bus
    }
    GROUP by ?name ?bus ?id
    ORDER by ?bus
    """

    def get_assignment_lookup_table(self):
        return self.assignment_lookup_table

    def create_assignment_lookup_table(self):
        der_em_mrid_per_bus_query_output = edmCore.gapps_session.query_data(self.der_em_mrid_per_bus_query_message)
        print("Bus query results:")
        print(der_em_mrid_per_bus_query_output)
        x = []
        for i in range(len(der_em_mrid_per_bus_query_output['data']['results']['bindings'])):
            x.append({'Name':der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['name']['value'], 'Bus':der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['bus']['value'], 'mRID': der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['id']['value']})
        self.assignment_lookup_table = x
        print(self.assignment_lookup_table)

    def assign_all_ders(self):
        self.assignment_table = self.assignment_lookup_table
        dersHistoricalDataInput.assign_der_s_to_der_em()

        print("DER Assignment complete.")
        print(self.association_table)

    def get_mRID_for_der_on_bus(self, Bus):
        print("Getting mRID for a der on bus:" )
        print(Bus)
        try:
            next_mrid_on_bus = next(item for item in self.assignment_table if item['Bus'] == str(Bus))
            mrid = next_mrid_on_bus['mRID']
            self.assignment_table = [i for i in self.assignment_table if not (i['mRID'] == mrid)]
        except StopIteration:
            print("FATAL ERROR: Attempting to assign a DER to a nonexistant DER-EM. The bus may be wrong, or may not contain enough DER-EMs. Verify test.")
            quit()
        print(next_mrid_on_bus)
        return(mrid)

class MCInputInterface:
    current_unified_input_request = None
    active_der_s_list = None
    test_DER_1_mrid = '_B1C7AD50-5726-4442-BA61-B8FA87C8E947'
    test_DER_2_mrid = '_2750969C-CBD5-41F4-BDCE-19287FBDCA71'
    test_DER_3_mrid = '_1720E0C8-A0CA-41BF-84DE-9847A17EBE26'


    def update_all_der_em_status(self):
        self.test_der_em()
        pass

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
        for i in self.current_unified_input_request:
            print(i)
            der_name_to_look_up = list(i.keys())
            der_name_to_look_up = der_name_to_look_up[0]
            print("DER Name to look up:")
            print(der_name_to_look_up)
            associated_der_em_mrid = derIdentificationManager.get_der_em_mrid(der_name_to_look_up)
            print("Associated DER EM mrid")
            print(associated_der_em_mrid)
            print(i[der_name_to_look_up])
            my_diff_build = DifferenceBuilder(edmCore.sim_mrid)
            my_diff_build.add_difference(associated_der_em_mrid, "PowerElectronicsConnection.p", int(i[der_name_to_look_up]), 0)
            message = my_diff_build.get_message()
            print(message)
            edmCore.gapps_session.send(input_topic, message)
        self.current_unified_input_request.clear()


class GOTopologyProcessor:
    topology_file_path = None
    topology_dict = {}
    inverse_topology_lookup_dict = {}
    bus_list = []
    group_list = []

    def import_topology_from_file(self):
        tree = ET.parse('topology.xml')
        root = tree.getroot()
        topology_map = []
        for i, val in enumerate(root):
            topological_input_row_key = list(root[i].attrib.values())[0]
            topological_input_row_vals = []
            for a, b in enumerate(root[i]):
                topological_input_row_vals.append(list(root[i][a].attrib.values()))
            topology_map_row = {topological_input_row_key: topological_input_row_vals}
            topology_map.append(topology_map_row)

        self.topology_dict = topology_map
        # print(topology_map)
        group_list = []
        bus_list = []

        for i in topology_map:
            group_list.append(list(i.keys())[0])
            bus_list.append(list(i.values()))

        self.group_list = group_list
        # print(group_list)

        for flatten_count in range(0, 3):
            bus_list = [x for l in bus_list for x in l]

        bus_list_final = []
        [bus_list_final.append(x) for x in bus_list if x not in bus_list_final]
        self.bus_list = bus_list
        # print(bus_list_final)

    # def parse_topology(self):
    #     pass

    def reverse_topology_dict(self):
        pass

    def get_group_members(self, group_input):
        for i in self.topology_dict:
            try:
                bus_return = i[group_input]
                bus_return = [x for l in bus_return for x in l]
                # print(bus_return)
            except KeyError:
                pass

    def get_groups_bus_is_in(self):
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
            # print("Current array time:")
            # print(self.timestamp_array)
        else:
            #print("skipping")
            pass

    def open_csv_file(self):
        print("Opening .csv file:")
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
