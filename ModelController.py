
import os
import ast
import csv
import time
# import json
import xmltodict
import pandas as pd
from dict2xml import dict2xml
from pprint import pprint as pp
from gridappsd import topics as t
import xml.etree.ElementTree as ET
from gridappsd.simulation import Simulation
from gridappsd import GridAPPSD, DifferenceBuilder

end_program = False

# ------------------------------------------------ Class Definitions ------------------------------------------------


class MCConfiguration:
    def __init__(self):
        self.mc_file_directory = r"/home/deras/Desktop/midrar_work_github/cimhub_psu_feeder/midrar_me/"
        self.config_file_path = self.mc_file_directory + r"Configuration/simulation_configuration.json"
        # midrar is not using the WH emulators. So remove the RWHDERS and its respective key.
        self.ders_obj_list = {
            'DERSHistoricalDataInput': 'dersHistoricalDataInput'
        }
        self.go_sensor_decision_making_manual_override = True
        self.manual_service_filename = "manually_posted_service_input.xml"
        self.output_log_name = 'Logged_Grid_State_Data/MeasOutputLogs'


class EDMCore:

    def __init__(self):
        #print(f"\n\n--------\n\nI am here in edmCore init func\n\n--------\n\n")
        self.gapps_session = None
        self.sim_session = None
        self.sim_start_time = None
        self.sim_current_time = None
        self.sim_mrid = None
        self.line_mrid = None
        self.config_parameters = None
        self.mrid_name_lookup_table = []
        self.cim_measurement_dict = []

    def get_sim_start_time(self):
        self.sim_start_time
        #print(f"\n\n--------\n\nI am here in edmCore get_sim_start_time\n\n{self.sim_start_time}\n\n--------\n\n")

        return self.sim_start_time

    def get_line_mrid(self):
        self.line_mrid
        #print(f"\n\n--------\n\nI am here in edmCore get line mrid func\n\n{self.line_mrid}\n\n--------\n\n")

        return self.line_mrid

    def sim_start_up_process(self):
        #print(f"\n\n--------\n\nI am here in edmCore startup process\n\n--------\n\n")

        self.connect_to_gridapps()
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
        derIdentificationManager.initialize_association_lookup_table()
        mcOutputLog.set_log_name()
        goSensor.load_manual_service_file()


    def load_config_from_file(self):
        #print(f"\n\n--------\n\nI am here in edmCore load config from file\n\n--------\n\n")

        with open(mcConfiguration.config_file_path) as f:
            config_string = f.read()
            self.config_parameters = ast.literal_eval(config_string)

    def connect_to_gridapps(self):
        #print(f"\n\n--------\n\nI am here in edmCore connect to gridappsd func\n\n--------\n\n")

        os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
        os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
        os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
        os.environ['GRIDAPPSD_PORT'] = '61613'

        # Connect to GridAPPS-D Platform
        self.gapps_session = GridAPPSD()
        assert self.gapps_session.connected

    def initialize_sim_mrid(self):

        self.sim_mrid = self.sim_session.simulation_id
        #print(f"\n\n--------\n\nI am here in edmCore initialize sim mrid\n\n--------\n\n{self.sim_mrid}")

    def initialize_line_mrid(self):

        self.line_mrid = self.config_parameters["power_system_config"]["Line_name"]
        #print(f"\n\n--------\n\nI am here in edmCore initialize line mrid\n\n--------\n\n{self.line_mrid}")

    def initialize_sim_start_time(self):

        self.sim_start_time = self.config_parameters["simulation_config"]["start_time"]
        #print(f"\n\n--------\n\nI am here in edmCore initialize sim start time\n\n--------\n\n{self.sim_start_time}")

    def connect_to_simulation(self):

        self.sim_session = Simulation(self.gapps_session, self.config_parameters)
        #print(f"\n\n--------\n\nI am here in edmCore connect to simulation\n\n--------\n\n")

    def create_objects(self):

        global mcOutputLog
        mcOutputLog = MCOutputLog()
        global mcInputInterface
        mcInputInterface = MCInputInterface()
        global dersHistoricalDataInput
        dersHistoricalDataInput = DERSHistoricalDataInput(mcConfiguration)
        global rwhDERS
        # rwhDERS = RWHDERS(mcConfiguration)
        global derAssignmentHandler
        derAssignmentHandler = DERAssignmentHandler()
        global derIdentificationManager
        derIdentificationManager = DERIdentificationManager()
        global goSensor
        goSensor = GOSensor()
        global goOutputInterface
        goOutputInterface = GOOutputInterface()

    def initialize_all_der_s(self):
        #print(f"\n\n------\n\nI am here initialize_all_der_s\n heading to hist data class.init_der_s\n\n-------\n\n")
        for key, value in mcConfiguration.ders_obj_list.items():
            eval(value).initialize_der_s()

    def start_simulation(self):
        #print(f"\n\n--------\n\nI am here in edmCore start_simulation\n\n--------\n\n")

        self.initialize_sim_start_time()
        self.sim_session.start_simulation()

    def establish_mrid_name_lookup_table(self):
        #print(f"\n\n--------\n\nI am here in edmCore establish mrid name lookup table\n\n--------\n\n")

        topic = "goss.gridappsd.process.request.data.powergridmodel"
        message = {
            "modelId": edmCore.get_line_mrid(),
            "requestType": "QUERY_OBJECT_MEASUREMENTS",
            "resultFormat": "JSON",
        }
        object_meas = edmCore.gapps_session.get_response(topic, message)
        self.mrid_name_lookup_table = object_meas['data']

        config_api_topic = 'goss.gridappsd.process.request.config'
        message = {
            'configurationType': 'CIM Dictionary',
            'parameters': {'model_id': edmCore.line_mrid}
        }
        cim_dict = edmCore.gapps_session.get_response(config_api_topic, message, timeout=20)
        measdict = cim_dict['data']['feeders'][0]['measurements']
        self.cim_measurement_dict = measdict
        # print("-------------- EDMCORE CIM_MEASUREMENT_DICT -------------------------")
        # pp(self.cim_measurement_dict)
        # print("-------------- EDMCORE CIM_MEASUREMENT_DICT -------------------------")
    def get_mrid_name_lookup_table(self):
        #print(f"\n\n--------\n\nI am here in edmCore get mrid name lookup table\n\n--------\n\n")
        """
        ACCESSOR METHOD: Returns the mrid_name_lookup_table.
        """
        return self.mrid_name_lookup_table

    def get_cim_measurement_dict(self):
        #print(f"\n\n--------\n\nI am here in edmCore get cim measurement dict\n\n--------\n\n")
        """
        ACCESSOR METHOD: Returns the cim_measurement.dict.
        """
        return self.cim_measurement_dict


class EDMTimeKeeper(object):
    """
    CALLBACK CLASS. GridAPPS-D provides logging messages to this callback class. on_message() filters these down
    to exclude everything except simulation timestep "incrementing to..." messages and simulation ending messages.
    Each time an incrementation message is received from GridAPPS-D, one second has elapsed. The Timekeeper increments
    the time each timestep; more importantly, it also calls all methods that are intended to run continuously during
    simulation runtime. perform_all_on_timestep_updates() updates the MC once per second, including receiving DER-S
    inputs, updating the DER-EMs, and updating the logs.

    Note: this does not include updating the grid state measurements. GridAPPS-D retrieves grid states for the
    measurement callbacks once every three seconds using a completely different communications pathway. As such,
    measurements and their processing are not handled by this class in any way.

    ATTRIBUTES:

        .sim_start_time: The (from config) simulation start timecode.

        .sim_current_time: The current timestamp. Initialized to the sim start time.

        .previous_log_message: A buffer containing the previous log message. Necessary to fix a double incrementation
               glitch caused by GridAPPS-D providing the same log multiple times.

        .edmCoreObj: edmCore is fed through an argument directly since it doesn't function properly as a global object.
    """

    def __init__(self, edmCoreObj):
        self.sim_start_time = edmCoreObj.get_sim_start_time()
        self.sim_current_time = self.sim_start_time
        self.previous_log_message = None
        self.edmCoreObj = edmCoreObj

    def on_message(self, sim, message):
        """
        CALLBACK METHOD: the "message" argument contains the full text of the Log messages provided by GridAPPS-D. This
        occurs for many reasons, including startup messages, errors, etc. We are only concerned with two types of
        messages: if the message contains the text "incrementing to ", that means one second (and thus one timestep) has
        elapsed, and if the message process status is "complete" or "closed", we know the simulation is complete and
        the MC should close out.
        """

        # on_message function definitions:

        def end_program():
            """
            Ends the program by closing out the logs and setting the global end program flag to true, breaking the
            main loop.
            """
            # mcOutputLog.close_out_logs()
            global end_program
            end_program = True

        def update_and_increment_timestep(log_message, self):
            """
            Increments the timestep only if "incrementing to " is within the log_message; otherwise does nothing.
            """
            if "incrementing to " in log_message:
                if log_message != self.previous_log_message:  # Msgs get spit out twice for some reason. Only reads one.
                    self.increment_sim_current_time()
                    print("\n\n\n--------- Current timestep:\t" + self.sim_current_time)
                    self.perform_all_on_timestep_updates()
                    self.previous_log_message = log_message

        # on_message() function body:

        log_message = message["logMessage"]
        process_status = message['processStatus']
        try:
            if process_status == 'COMPLETE' or process_status == 'CLOSED':
                end_program()
            else:
                update_and_increment_timestep(log_message, self)
        except KeyError as e:   # Spits out the log message for troubleshooting if something weird happens.
            print(e)
            print("KeyError!")
            print(message)

    def increment_sim_current_time(self):
        """
        Increments the current simulation time by 1.
        """
        current_int_time = int(self.sim_current_time)
        current_int_time += 1
        self.sim_current_time = str(current_int_time)

    def get_sim_current_time(self):
        """
        ACCESSOR: Returns the current simulation time. (Not real time.)
        """
        return self.sim_current_time

    def perform_all_on_timestep_updates(self):
        """
        ENCAPSULATION: Calls all methods that update the system each timestep (second). New processes should be added
        here if they need to be ongoing, I.E. once per second through the simulation.

        NOTE: DOES NOT INCLUDE MEASUREMENT READING/PROCESSING. Those are done once every three seconds due to the way
        GridAPPS-D is designed and are independent of the simulation timekeeper processes. See EDMMeasurementProcessor.
        """
        #print("\n\n--------------- Performing on-timestep updates --------------------\n\n")
        self.edmCoreObj.sim_current_time = self.sim_current_time
        mcInputInterface.update_all_der_s_status()
        mcInputInterface.update_all_der_em_status()
        mcOutputLog.update_logs()
        goSensor.make_service_request_decision()
        goOutputInterface.get_all_posted_service_requests()
        goOutputInterface.send_service_request_messages()
        #print("\n\n--------------- Done with on-timestep updates --------------------\n\n")


class EDMMeasurementProcessor(object):
    """
    CALLBACK CLASS: once per three seconds (roughly), GridAPPS-D provides a dictionary to the on_message() method
    containing all of the simulation measurements by mRID including the magnitude, angle, etc. The measurement processor
    parses that dictionary into something more useful to the MC, draws more valuable information from the model, gets
    association and location data from the input branch, and appends it to the dictionary to produce something usable
    by the GO and the logging class.

    NOTE: the API for measurements and timekeeping are completely separate. The MC as a whole is synchronized with the
    timekeeping class, but measurement processes are done separately. This is why logs will have repeated values: the
    logs are part of the MC and thus update once per second, but the grid states going IN to the logs are only updated
    once per three seconds.

    ATTRIBUTES:
        .measurement_timestamp: The timestamp of the most recent set of measurements as read from the GridAPPS-D
            message. NOTE: Currently unused, but might be useful for future log revisions.

        .current_measurements: Contains the measurements taken from the GridAPPS-D message. Written in the function
            parse_message_into_current_measurements.

        .mrid_name_lookup_table: Read from EDMCore. Used to append informative data to each measurement.

        .measurement_lookup_table: Read from EDMCore. Used to append (different) information to each measurement.

        .measurement_mrids: Measurement dictionaries provided by GridAPPS-D use mRIDs as keys for each measurement.
            This contains a list of those keys and is used to replace those mRIDs with human-readable names.

        .measurement_names: A list of human-readable measurement names. See measurement_mrids.

        .assignment_lookup_table: Read from DERAssignmentHandler. Used to append DER-S to DER-EM association data to
            each measurement for logging and troubleshooting purposes.
    """

    def __init__(self):
        self.measurement_timestamp = None
        self.current_measurements = None
        self.mrid_name_lookup_table = []
        self.measurement_lookup_table = []
        self.measurement_mrids = []
        self.measurement_names = []
        self.assignment_lookup_table = []

    def on_message(self, headers, measurements):
        """
        CALLBACK METHOD: receives the measurements once every three seconds, and passes them to the parsing method.
        """
        self.parse_message_into_current_measurements(measurements)

    def get_current_measurements(self):
        """
        ACCESSOR: Returns the current fully processed measurement dictionary.
        """
        return self.current_measurements

    def parse_message_into_current_measurements(self, measurement_message):
        """
        The measurement message from GridAPPS-D is pretty ugly. This method pulls out just the stuff we need, and then
        calls methods to append names, association/location info, etc. Basically, this turns the raw input data into
        the fully formatted edmMeasurementProcessor.current_measurements dictionary which is passed to the logger and GO
        """
        
        self.current_measurements = measurement_message['message']['measurements']
        # pp(measurement_message)
        self.measurement_timestamp = measurement_message['message']['timestamp']
        self.append_names()
        self.append_association_data()

    def append_names(self):
        """
        Adds a bunch of extra important information to each measurement's value dictionary.
        """
        self.mrid_name_lookup_table = edmCore.get_mrid_name_lookup_table()
        self.measurement_lookup_table = edmCore.get_cim_measurement_dict()
        self.measurement_mrids = self.current_measurements
        # print("---------------------------------------==========----------------")
        # print(self.measurement_mrids)
        # print("---------------------------------------==========----------------")
        self.measurement_mrids = self.current_measurements.keys()
        
        for i in self.measurement_mrids:
            try:
                lookup_mrid = next(item for item in self.mrid_name_lookup_table if item['measid'] == i)
                
            except StopIteration:
                print(f"\n\n-------- lookup_mrid --------\n\n{lookup_mrid}")
            lookup_name = lookup_mrid['name']
            self.measurement_names.append(lookup_name)

        self.measurement_mrids = dict(zip(list(self.measurement_mrids), self.measurement_names))
        
        for key, value in self.measurement_mrids.items():
            try:
                self.current_measurements[key]['Measurement name'] = value
                measurement_table_dict_containing_mrid = next(item for item in self.measurement_lookup_table
                                                              if item['mRID'] == key)
                self.current_measurements[key]['Meas Name'] = measurement_table_dict_containing_mrid['name']
                self.current_measurements[key]['Conducting Equipment Name'] = measurement_table_dict_containing_mrid[
                    'ConductingEquipment_name']
                self.current_measurements[key]['Bus'] = measurement_table_dict_containing_mrid[
                    'ConnectivityNode']
                self.current_measurements[key]['Phases'] = measurement_table_dict_containing_mrid[
                    'phases']
                self.current_measurements[key]['MeasType'] = measurement_table_dict_containing_mrid[
                    'measurementType']
            except StopIteration:
                print("\n\n ---------- Measurements updated with amplifying information ---------- \n\n")

    def append_association_data(self):
        """
        Appends association data.
        """
        self.assignment_lookup_table = derAssignmentHandler.get_assignment_lookup_table()
        for item in self.assignment_lookup_table:
            original_name = item['Name']
            # print(f"\n\n--------------\n\noriginal_name\n\n")
            # print(f"%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n{original_name}\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n")
            # formatted_name = original_name[:-len('_Battery')]
            formatted_name = original_name
            # print(f"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n")
            # print(formatted_name)
            # print(f"\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n")
            item['DER-EM Name'] = formatted_name

        for key, value in self.current_measurements.items():
            # print(f"\n\n-=-=-=-=-=-=-=-=-=-=-=-= KEY -=-=-=-=-=-=-=-=-=-=-=-=-=-=\n\n")
            # print(key)
            # print(f"\n\n-=-=-=-=-=-=-=-=-=-=-=-= VALUE -=-=-=-=-=-=-=-=-=-=-=-=-=-=\n\n")
            # print(value)
            try:
                assignment_dict_with_given_name = next(item for item in self.assignment_lookup_table if
                                                       item['DER-EM Name'] == self.current_measurements[key][
                                                           'Conducting Equipment Name'])
                self.current_measurements[key]['Inverter Control mRID'] = assignment_dict_with_given_name['mRID']
                input_name = derIdentificationManager.get_meas_name(assignment_dict_with_given_name['mRID'])
                self.current_measurements[key]['Input Unique ID'] = input_name
            except StopIteration:
                pass


class DERSHistoricalDataInput:
    """
    The Historical Data DER-S. Sometimes referred to as "manual input", this DER-S serves as a simple method to
    update DER-EMs manually at certain times with specific values, allowing the test engineer to write in grid states
    as needed by each simulation. Since DER-EMs are generic models, each historical data input could represent a single
    DER, groups of DERs, or even more abstract ideas such as massive power excursions.

    The input is a single .csv file, contained in the DERSHistoricalData Inputs folder. This .csv is timestamped and
    in a specific format; after the timestamp column, columns are in pairs, with each pair representing Power and Bus
    for each DER-EM. The bus is used for assignment, at which point the values are associated to DER-EMs by header
    names.

    Otherwise, it functions like any other DER-S: it has an initialization process, an assignment process, and on
    timestep updates.

    ATTRIBUTES:
        .der_em_input_request: Contains the new DER-EM states for this timestep, already parsed and put into list
           format by the function. The list is so multiple DER-EMs can be updated per timestep.

        .input_file_path: The folder in which the DERSHistoricalDataInput files are located.

        .input_table: The input files are in .csv format; the csv reader reads these files into a table here.

        .list_of_ders: The DER names read from the header of the input table.

        .location_lookup_dictionary: A dictionary associating the DER unique identifiers with the bus they should
           be assigned to.
    """
    def __init__(self, mcConfiguration):
        
        #print("----\n\nI am here in DERSHistoricalData Inpu, initialize_der_s\n\n-----")
        self.der_em_input_request = []
        self.historical_data_file_path = mcConfiguration.mc_file_directory + r"DERSHistoricalDataInput/psu_feeder_ders_data.csv"
        self.input_table = None
        self.list_of_ders = []
        self.location_lookup_dictionary = {}

    def initialize_der_s(self):
        #print("----\n\nI am here in DERSHistoricalData Inpu, initialize_der_s\n\n-----")
        """
        This function (with this specific name) is required in each DER-S used by the ME. The EDMCore's initialization
        process calls this function for each DER-S activated in MCConfig to perform initialization tasks. This does not
        include DER-EM assignment (see assign_der_s_to_der_em). In this case, all this function does is call
        the read_input_file() function. See below.
        """
        self.read_input_file()

    def get_input_request(self):
        #print("----\n\nI am here in get_input_request\n\n-----")
        """
        This function (with this specific name) is required in each DER-S used by the ME. Accessor function that calls
        for an updated input request, then returns the updated request for use by the MCInputInterface
        """
        self.update_der_em_input_request()
        return self.der_em_input_request

    def assign_der_s_to_der_em(self):
        """
        This function (with this specific name) is required in each DER-S used by the ME. The DERAssignmentHandler
        calls this function for each DER-S activated in MCConfig. This function's purpose is to take unique identifiers
        from each "DER input" for a given DER-S and "associate" them with the mRIDs for DER-EMs in the model. This is
        done using locational data: I.E. a specific DER input should be associated with the mRID of a DER-EM on a given
        bus.

        Midrar Notes:

        - The input_table[0] variable prints all der_loc and der_mag values for a single timestep.
        
        - [(location_lookup_dictionary[i])] returns a dictionary that looks like:
            {'DER0_loc':'DER0_mag',
            'DER1_loc':'DER1_mag', 
            }
        and so forth.

        - In Sean's ME version, der_being_assigned[i] returns the bus location, which is 632
        """
        # print(f"\n\n----------\n\nI am here in dersHistoricalData class, assign_der_s_to_der_input_request\n\n----------\n\n")
        for i in self.list_of_ders:
            der_being_assigned = {}
            # print('\ninput table [0] ---> ',self.input_table[0])
            # print('\nlocation_lookup_table[i] ---> ', self.location_lookup_dictionary[i])
            der_being_assigned[i] = self.input_table[0][(self.location_lookup_dictionary[i])]
            # print('\nder_being_assigned --->', der_being_assigned[i])
            der_being_assigned[i] = derAssignmentHandler.get_mRID_for_der_on_bus(der_being_assigned[i])
            assigned_der = dict([(value, key) for value, key in der_being_assigned.items()])
            # print('\nassigned_der --->', assigned_der)
            derAssignmentHandler.append_new_values_to_association_table(assigned_der)

    def open_input_file(self):
        """
        Opens the historical data input file, read it as a .csv file, and parses it into a list of dicts.
        """
        with open(self.historical_data_file_path) as csvfile:
            r = csv.DictReader(csvfile)
            x = []
            for row in r:
                row = dict(row)
                x.append(row)
        self.len_der_s_historical_data_input = len(x)
        return x
        

    def read_input_file(self):
        # print("----\n\nI am here in read_input_file line 600\n\n-----")
        """
        Reads and parses the input file. Places all the input information in input_table. Also, parses the
        .csv file to determine the names and locations of each DER: when the timestamp column is removed, odd column
        headers are names and even headers are their associated locations. These lists are converted to a list
        of dictionaries to be passed to the assignment handler (which takes the locations for each DER name and assigns
        a DER-EM mRID at the proper location to the name, this allows the MC to provide updated DER states to the DER-EM
        without requiring the inputs to know DER-EM mRIDs.)
        """
        self.input_table = self.open_input_file()
        first_row = next(item for item in self.input_table)
        first_row = dict(first_row)
        first_row.pop('Time')
        log_der_keys = list(first_row.keys())
        for i in range(len(log_der_keys)):
            if i % 2 == 0:
                der_name = log_der_keys[i]
            else:
                der_loc = log_der_keys[i]
                self.location_lookup_dictionary[der_name] = der_loc

        self.list_of_ders = list(self.location_lookup_dictionary.keys())

    def update_der_em_input_request(self):
        # print("----\n\nI am here in update_der_em_input_request\n\n-----")
        """
        Checks the current simulation time against the input table. If a new input exists for the current timestep,
        it is read, converted into an input dictionary, and put in the current der_input_request
        (see MCInputInterface.get_all_der_s_input_requests() )
        """
        self.der_em_input_request.clear()
        try:
            input_at_time_now = next(item for item in self.input_table if int(edmCore.sim_current_time) <=
                                     int(item['Time']) < (int(edmCore.sim_current_time) + 1))
            #print("\n\n --------- Updating DER-EMs from historical data --------- \n\n")
            input_at_time_now = dict(input_at_time_now)
            input_at_time_now.pop('Time')
            for i in self.list_of_ders:
                self.der_em_input_request.append({i: input_at_time_now[i]})
        except StopIteration:
            #print("\n\n --------- End of input data ---------\n\n")
            return


class DERIdentificationManager:
    """
    This class manages the input association lookup table generated by the DERSAssignmentHandler. The accessor methods
    allow input unique IDs to be looked up for a given DER-EM mRID, or vice versa. The table is generated during the
    assignment process (see DERAssignmentHandler).

    ATTRIBUTES:
        .association_lookup_table: a list of dictionaries containing association data, read from the
            DERAssignmentHandler after the startup process is complete. Used to connect the unique identifiers of
            DER inputs (whatever form they might take) to mRIDs for their assigned DER-EMs.
    """
    def __init__(self):
        self.association_lookup_table = None

    def get_meas_name(self, mrid):
        """
        ACCESSOR FUNCTION: Returns a unique identifier for a given DER-EM mRID. If none found, the DER-EM was never
        assigned, and 'Unassigned' is returned instead.
        """
        for i in self.association_lookup_table:
            for key, value in i.items():
                if value == mrid:
                    input_unique_id = key
        try:
            return input_unique_id
        except UnboundLocalError:
            return 'Unassigned'

    def get_der_em_mrid(self, name):
        """
        ACCESSOR FUNCTION: Returns the associated DER-EM control mRID for a given input unique identifier. Unlike
        get_meas_name(), if none is found that signifies a critical error with the DERSAssignmentHandler.
        """
        x = next(d for i, d in enumerate(self.association_lookup_table) if name in d)
        return x[name]

    def initialize_association_lookup_table(self):
        """
        Retrieves the association table from the assignment handler.
        """
        self.association_lookup_table = derAssignmentHandler.association_table


class DERAssignmentHandler:
    """
    This class is used during the MC startup process. DER-S inputs will not know the mRIDs of DER-EMs since those
    are internal to the EDM. As such, a process is required to assign each incoming DER input to an appropriate DER-EM
    mRID, so that it's states can be updated in the model. Each DER-S DER unit requires a unique identifier (a name, a
    unique number, etc.) and a "location" on the grid, generally the bus it's located on. The assignment handler
    receives as input a list of {uniqueID:location} dictionaries, uses the location values to look up the DER-EMs on the
    appropriate bus, and assigns each unique identifier to an individual DER-EM. These associations are passed to the
    Identification Manager; during the simulation, new inputs from each unique ID sent to the input manager, which
    automatically looks up the appropriate mRID for the associated DER-EM and sends the inputs there.

    ATTRIBUTES:
        .assignment_lookup_table: contains a list of dictionaries containing mRID, name, and Bus of each DER-EM within
            the model.

        .assignment_table: a redundant assignment_lookup_table, used during the assignment process in order to prevent
            modification to the original assignment lookup table (which will still need to be used by the output
            branch).

        .association_table: Contains association data provided by each DER-S class, for use by the
            DERIdentificationManager.

        .der_em_mrid_per_bus_query_message: SPARQL Query used to gather the DER-EM info for the assignment tables from the model database.
    """
    def __init__(self):
        self.assignment_lookup_table = None
        self.assignment_table = None
        self.association_table = []
        self.der_em_mrid_per_bus_query_message = f'''
        PREFIX r: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX c: <http://iec.ch/TC57/CIM100#>
        SELECT ?class ?type ?name ?bus ?phases ?eqtype ?eqname ?eqid ?trmid ?id WHERE {{
        VALUES ?fdrid {{"{edmCore.line_mrid}"}}  # psu_feeder
        ?eq c:Equipment.EquipmentContainer ?fdr.
        ?fdr c:IdentifiedObject.mRID ?fdrid.
        {{ ?s r:type c:Discrete. bind ("Discrete" as ?class)}}
          UNION
        {{ ?s r:type c:Analog. bind ("Analog" as ?class)}}
        ?s c:IdentifiedObject.name ?name .
        ?s c:IdentifiedObject.mRID ?id .
        ?s c:Measurement.PowerSystemResource ?eq .
        ?s c:Measurement.Terminal ?trm .
        ?s c:Measurement.measurementType ?type .
        ?trm c:IdentifiedObject.mRID ?trmid.
        ?eq c:IdentifiedObject.mRID ?eqid.
        ?eq c:IdentifiedObject.name ?eqname.
        ?eq r:type ?typeraw.
         bind(strafter(str(?typeraw),"#") as ?eqtype)
        ?trm c:Terminal.ConnectivityNode ?cn.
        ?cn c:IdentifiedObject.name ?bus.
        ?s c:Measurement.phases ?phsraw .
         {{bind(strafter(str(?phsraw),"PhaseCode.") as ?phases)}}
        }} ORDER BY ?class ?type ?name
        '''
        #print(f"\n\n------\n\nQuery to gather DER-EM Data\n\n{self.der_em_mrid_per_bus_query_message}\n\n------\n\n")

    def get_assignment_lookup_table(self):
        """
        ACCESSOR: Returns the assignment lookup table. Used in the message appendage process.
        """
        return self.assignment_lookup_table

    def create_assignment_lookup_table(self):
        #print("\n\n-------\n\nI am here in create_assignment_lookup_able\n\n-------\n\n")
        """
        Runs an extended SPARQL query on the database and parses it into the assignment lookup table: that is, the names
        and mRIDs of all DER-EMs on each bus in the current model.
        """
        der_em_mrid_per_bus_query_output = edmCore.gapps_session.query_data(self.der_em_mrid_per_bus_query_message)
        
        x = []
        for i in range(len(der_em_mrid_per_bus_query_output['data']['results']['bindings'])):
            if (der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['name']['value'].startswith('EnergyConsumer')) and (der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['bus']['value'].startswith('trip_load')):
                curr_dict = {'Name':der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['name']['value'].split("r_")[1],
                             'Bus':der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['bus']['value'],
                             'mRID':der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['eqid']['value']}
                if curr_dict not in x:
                    x.append(curr_dict)
        self.assignment_lookup_table = x

    def assign_all_ders(self):
        #print(f"\n\n-------\n\nI am here in derassignment handler, assign all ders\n\n-------\n\n")
        #print(f"\n\n-------\n\nLet us look at the assignment table\n\n-------\n\n")
        """
        Calls the assignment process for each DER-S. Uses the DER-S list from MCConfiguration, so no additions are
        needed here if new DER-Ss are added.
        """
        self.assignment_table = self.assignment_lookup_table

        # with open ('assignment_table_derAssignmentHandler_assign_all_ders.json', 'w') as output:
        #     json.dump(self.assignment_table, output, indent=4)

        # Object list contains string names of objects. eval() lets us use these to call the methods for the proper obj
        for key, value in mcConfiguration.ders_obj_list.items():
            eval(value).assign_der_s_to_der_em()

    def get_mRID_for_der_on_bus(self, Bus):
        """
        For a given Bus, checks if a DER-EM exists on that bus and is available for assignment. If so, returns its mRID
        and removes it from the list (so a DER-EM can't be assigned twice).
        """
        #print(f"\n\n-------\n\nI am here in derassignmenthandler, get mRID for der on bus\n\n-------\n\n")
        #print(Bus)
        
        try:
            
            next_mrid_on_bus = next(item for item in self.assignment_table if item['Bus'] == str(Bus))
            mrid = next_mrid_on_bus['mRID']
            self.assignment_table = [i for i in self.assignment_table if not (i['mRID'] == mrid)]
        except StopIteration:
            print("FATAL ERROR: Attempting to assign a DER to a nonexistent DER-EM. "
                  "The bus may be wrong, or may not contain enough DER-EMs. Verify test.")
            quit()
        #print(f"\n\n -------- next_mrid_on_bus -------- \n\n{next_mrid_on_bus}")
        
        return mrid

    def append_new_values_to_association_table(self, values):
        """
        Used by DER-S classes to add new values to the association table during initialization.
        """
        self.association_table.append(values)
        # print('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
        # print(self.association_table)
        # print('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')


class MCInputInterface:
    """
    Input interface. Receives input messages from DER-Ss, retrieves the proper DER-EM input mRIDs for each input from
    the Identification Manager, and delivers input messages to the EDM that update the DER-EMs with the new states.

    ATTRIBUTES:
        .current_unified_input_request: A list of all input requests currently being provided to the Input Interface
            by all active DER-Ss.
    """

    def __init__(self):
        self.current_unified_input_request = []

    def update_all_der_em_status(self):
        """
        Currently, calls the update_der_ems() method. In the future, may be used to call methods for different input
        types; a separate method may be written for voltage inputs, for instance, and called here once per timestep.
        """
        self.update_der_ems()
        pass

    def update_all_der_s_status(self):
        """
        Gets the DER-S input requests.
        """
        self.get_all_der_s_input_requests()

    def get_all_der_s_input_requests(self):
        """
        Retrieves input requests from all DER-Ss and appends them to a unified input request.
        """
        online_ders = mcConfiguration.ders_obj_list
        # print(f"\n\n------ ONLINE DERs -----\n\n {online_ders} --------")
        self.current_unified_input_request.clear()
        for key, value in mcConfiguration.ders_obj_list.items():
            # print(f"\n\n------ value in der_obj_list -----\n\n {value} \n\n--------")
            self.current_unified_input_request = self.current_unified_input_request + eval(value).get_input_request()
        print(f"\n\n------ Current unified input request: ------\n\n {self.current_unified_input_request} --------")
        # print(self.current_unified_input_request)

    def update_der_ems(self):
        """
        Reads each line in the unified input request and uses the GridAPPS-D library to generate EDM input messages for
        each one. The end result is the inputs are sent to the associated DER-EMs and the grid model is updated with
        the new DER states. This will be reflected in future measurements.
        """
        input_topic = t.simulation_input_topic(edmCore.sim_mrid)
        my_diff_build = DifferenceBuilder(edmCore.sim_mrid)
        for i in self.current_unified_input_request:
            der_name_to_look_up = list(i.keys())
            der_name_to_look_up = der_name_to_look_up[0]
            associated_der_em_mrid = derIdentificationManager.get_der_em_mrid(der_name_to_look_up)
            my_diff_build.add_difference(associated_der_em_mrid, "EnergyConsumer.p",
                                         int(i[der_name_to_look_up]), 0)
        message = my_diff_build.get_message()
        edmCore.gapps_session.send(input_topic, message)
        my_diff_build.clear()
        self.current_unified_input_request.clear()


class GOTopologyProcessor:
    """
    'Topology' refers to where things are on the grid in relation to one another. In its simplest form, topology can
    refer to what bus each DER-EM is on. However, GOs and GSPs may view topology in more complex forms, combining
    buses into branches, groups, etc. More complex topologies are stored in xml files and read into the MC by this
    class; the XLM contains each "group" and whatever buses are members of it. This class will then be able to

    Topological processing is not required in the early stages of testing, so this class has not been fully implemented
    and many of its functions are currently unused.
    """
    def __init__(self):
        self.topology_dict = {}
        self.bus_list = []
        self.group_list = []

    def import_topology_from_file(self):
        """
        Reads the topology xml file. This needs to be generated prior to the simulation and will be used by both the
        ME and the DERMS in use (ex. the GSP).
        """
        tree = ET.parse('Configuration/topology.xml')
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
        group_list = []
        bus_list = []
        for i in topology_map:
            group_list.append(list(i.keys())[0])
            bus_list.append(list(i.values()))
        self.group_list = group_list
        for flatten_count in range(0, 3):
            bus_list = [x for item in bus_list for x in item]
        bus_list_final = []
        [bus_list_final.append(x) for x in bus_list if x not in bus_list_final]
        self.bus_list = bus_list

    def reverse_topology_dict(self):
        """
        Not implemented.
        """
        pass

    def get_group_members(self, group_input):
        """
        Unused. Returns all buses contained in a given group.
        """
        for i in self.topology_dict:
            try:
                bus_return = i[group_input]
                bus_return = [x for item in bus_return for x in item]
                # print(bus_return)
                return bus_return
            except KeyError:
                pass

    def get_groups_bus_is_in(self):
        """
        Not implemented. Returns all groups a given bus is a member of.
        """
        pass


class GOSensor:
    """
    This class retrieves fully formatted grid states from the measurement processor, filters them down to necessary
    information, and makes determinations (automatically or manually) about grid services, whether they're required,
    happening satisfactorily, etc. These determinations are sent to the output API to be communicated to the DERMS.

    NOTE: In the current state of the ME, only Manual Mode is implemented. Automatic Mode requires development of GO
    threshold detection algorithms that, while more realistic, do not support the current goal of functionally testing
    a DERMS.

    ATTRIBUTES:
        .current_sensor_states: Grid states read into the sensor. Automatic mode only. Not currently implemented.

        .service_request_decision: Determination whether a grid service is needed. Automatic mode. Not implemented.

        .posted_service_list: List of posted service objects. Used by both Automatic and Manual modes.

        .manual_service_xml_data: In Manual Mode, the data contained within the manual service xml file. To be parsed
            and posted service objects generated from this data.
    """
    def __init__(self):
        self.current_sensor_states = None
        self.service_request_decision = None
        self.posted_service_list = []
        self.manual_service_xml_data = {}

    def update_sensor_states(self):
        """
        Retrieves measurement data from the Measurement Processor. The measurements are organized by topological group.
        This is only used by AUTOMATIC MODE. Not currently implemented.
        """
        pass

    def make_service_request_decision(self):
        """
        Performs the following once per timestep.
current_unified_input_request
        In MANUAL MODE (override is True):
            Instantiates a grid service
        In AUTOMATIC MODE (override is False):
            Will call code to make grid service determination. Currently not implemented.
        """
        if mcConfiguration.go_sensor_decision_making_manual_override is True:
            self.manually_post_service(edmTimekeeper.get_sim_current_time())
        elif mcConfiguration.go_sensor_decision_making_manual_override is False:
            pass
        else:
            print("Service request failure. Wrong input.")

        pass

    def load_manual_service_file(self):
        """
        MANUAL MODE: Reads the manually_posted_service_input.xml file during MC initialization and loads it into
        a dictionary for later use.
        """
        input_file = open(mcConfiguration.manual_service_filename, "r")
        data = input_file.read()
        input_file.close()
        self.manual_service_xml_data = xmltodict.parse(data)

    def manually_post_service(self, sim_time):
        """
        Called by make_service_request_decision() when in MANUAL mode. Reads the contents of the manual service
        dictionary, draws all relevant data points for each service, and instantiates a GOPostedService object for each
        one, appending the objects to a list.
        """
        for key, item in self.manual_service_xml_data['services'].items():
            # print(item)
            if int(item['start_time']) == int(sim_time):
                name = str(key)
                group_id = item["group_id"]
                service_type = item["service_type"]
                interval_duration = item["interval_duration"]
                interval_start = item["interval_start"]
                power = item["power"]
                ramp = item["ramp"]
                price = item["price"]
                start_time = item["start_time"]
                self.posted_service_list.append(GOPostedService(
                    name, group_id, service_type, interval_start, interval_duration, power, ramp, price))
                # print("---------------- \n\n\n\nManually posting service, name ----------------:")
                # print(name)


class GOOutputInterface:
    """
    API between the MC and a DERMS. Must be customized to the needs of the DERMS. Converts determinations and feedback
    data to message formats the DERMS requires/can use, and delivers them.

    ATTRIBUTES:
        .current_service_requests: A list of posted services. These are the services that are being requested, or are
            currently being executed. Can come from either Automatic or Manual Decision making. See GOPostedService.
    """
    current_service_requests = []

    def get_all_posted_service_requests(self):
        """
        Retrieves the service message data from each posted service (see the GOPostedService.get_service_message_data()
        method for more detail). Appends the data in the proper list-of-dict format to current_service_requests.

        Note: In the current implementation, it may seem redundant to read data from an xml file into dictionaries,
        package the data into object, and extract the data back into identical dictionaries; however, this is important
        to ensure that the process is decoupled. A different DERMS or even a more advanced ME-GSP API might not allow
        for such direct input formats.
        """
        for item in goSensor.posted_service_list:
            if item.get_status() is False:
                print("Posting...")
                self.current_service_requests.append(item.get_service_message_data())
                print(item.get_service_message_data())
                item.set_status(True)
            else:
                print("----------------All already posted----------------")
                #print(".")

    def generate_service_messages(self):
        """
        Converts the current_service_requests list of dicts into a proper xml format. Used by the xml writed in
        send_service_request_messages().
        """
        request_out_xml = '<services>\n'
        service_serial_num = 1
        for item in self.current_service_requests:
            print("Test1")
            # print(dict2xml(item))
            request_out_xml = request_out_xml + '<service' + str(service_serial_num) + '>\n'
            request_out_xml = request_out_xml + dict2xml(item) + '\n'
            request_out_xml = request_out_xml + '</service' + str(service_serial_num) + '>\n'
            service_serial_num = service_serial_num + 1
        request_out_xml = request_out_xml + '</services>'
        # request_out_xml = dict2xml(self.current_service_requests)
        # print("----------------\n\nCurrent Service Requests\n\n----------------")
        # print(request_out_xml)
        return request_out_xml

    def send_service_request_messages(self):
        """
        Writes the current service request messages to an xml file, which will be accessed by the GSP for its service
        provisioning functions.
        """
        xmlfile = open("Outputs To DERMS/OutputtoGSP.xml", "w")
        xmlfile.write(self.generate_service_messages())
        xmlfile.close()


class MCOutputLog:
    """
    Generates .csv logs containing measurements from the measurement processor. Updates (writes a line) once per
    timestep.

    ATTRIBUTES:
        .csv_file: Contains the csv file object (see open_csv_file())

        .log_name: The log name, taken from MCConfiguration during initialization.

        .mrid_name_lookup_table: a table of mRIDs and their respective plain english names, used to create the log
            headers. Taken from edmCore.get_mrid_name_lookup_table().

        .header_mrids: a list of mRIDs for each measurement point, used (invisibly) in the header to write logs.

        .header_names: the plain english versions of the header names.

        .csv_dict_writer: The dictionary writer object, used to write the .csv logs.

        .timestamp_array: A list of all timestamps for the logs. Appended at the end of simulation.

        .current_measurement: The dictionary containing the current set of measurements.

        .is_first_measurement: Flags functions that should only run once at the start of logging (such as opening
           the log files, setting up the header, etc.)

    """

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
        self.message_size = 0
        self.file_num = 0


    def update_logs(self):
        """
        During the first measurement, performs housekeeping tasks like opening the file, setting the name, translating
        the header to something readable, and writing the header. On all subsequent measurements, it writes a row of
        measurements to the logs and appends a new timestamp to the timestamp array.

        Note: The first timestep in the logs will be several seconds after the actual simulation start time.
        """
        self.current_measurement = edmMeasurementProcessor.get_current_measurements()
        if self.current_measurement:
            print("Updating logs...")
            if (self.is_first_measurement is True):
                self.message_size = 0
                print("First measurement routines...")
                self.set_log_name()
                self.open_csv_file()
                self.mrid_name_lookup_table = edmCore.get_mrid_name_lookup_table()
                self.translate_header_names()
                self.open_csv_dict_writer()
                self.write_header()
                self.is_first_measurement = False
            self.write_row()
            self.message_size_checkpoint()
            self.timestamp_array.append(edmTimekeeper.sim_current_time)
        else:
            pass

    def message_size_checkpoint (self):
        
        self.message_size +=1
        print('Current message size --->', self.message_size)
        if self.message_size > 120:
            print('Message size threshold reached!', self.message_size)
            print(f"Closing file ---> {mcConfiguration.output_log_name}_{self.file_num}.csv")
            self.is_first_measurement = True
            self.message_size = 0
            self.close_out_logs()
    
    def open_csv_file(self):
        """
        Opens the .csv file.
        """
        print("Opening .csv file:")
        self.csv_file = open(self.log_name, 'w')

    def open_csv_dict_writer(self):
        """
        Opens the dict writer used to write rows. Note that the headers used are the measurement mRIDs; the plain
        English names are a visual effect only.
        """
        self.csv_dict_writer = csv.DictWriter(self.csv_file, self.header_mrids)

    def close_out_logs(self):
        """
        Closes the log file and re-appends the timestamps.
        """
        self.csv_file.close()
        # self.append_timestamps()

    def translate_header_names(self):
        """
        Looks up the plain english names for the headers and provides them to a dictionary for use by write_header().
        """
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
        """
        Writes the log header.
        """
        self.csv_dict_writer.writerow(self.header_mrids)

    def write_row(self):
        """
        Writes a row of measurements to the logs.
        """
        self.csv_dict_writer.writerow(self.current_measurement)

    def set_log_name(self):
        """
        Sets the log name based on the MCConfiguration settings.
        """
        self.file_num += 1
        self.log_name = f"{mcConfiguration.output_log_name}_{self.file_num}.csv"

    def append_timestamps(self):
        """
        Uses the pandas library to append the timestamp column to the logs. This is the most convenient way to handle
        timekeeping while making sure to use the simulation time rather than the measurement time.
        """
        csv_input = pd.read_csv(self.log_name)
        self.timestamp_array = pd.to_datetime(self.timestamp_array, unit='s')
        csv_input['Timestamp'] = self.timestamp_array
        move_column = csv_input.pop('Timestamp')
        csv_input.insert(0, 'Timestamp', move_column)
        csv_input.to_csv(self.log_name, index=False)


class GOPostedService:
    """
    This class is (currently) the only class that can get instantiated more than once per simulation. It contains
    service request data required to communicate with the DERMS. This data informs the DERMS of the type,
    location, and parameters of a single service it wants to request from the DERMS. These service requests are then
    'posted' to a list in the GOSensor class, which is read by the GOOutputInterface class and processed into the
    communication format or protocol necessary for GO-DERMS communications (currently, an xml text file stored in the
    /Outputs to DERMS/ folder.)

    The attributes and accessor methods are mostly self-explanatory; the major points of interest are the fact that it
    stores whatever data is needed by the DERMS, and that there is a function that returns this data in dictionary
    format.
    """
    def __init__(self, service_name="Undefined", group_id=0, service_type="Undefined", interval_start=0,
                 interval_duration=0, power=0, ramp=0, price=0):
        self.service_name = service_name
        self.group_id = group_id
        self.service_type = service_type
        self.interval_start = interval_start
        self.interval_duration = interval_duration
        self.power = power
        self.ramp = ramp
        self.price = price
        self.status = False

    def get_service_name(self):
        return self.service_name

    def get_group_id(self):
        return self.group_id

    def get_service_type(self):
        return self.service_type

    def get_interval_start(self):
        return self.interval_start

    def get_interval_duration(self):
        return self.interval_duration

    def get_power(self):
        return self.power

    def get_price(self):
        return self.price

    def get_status(self):
        return self.status

    def set_status(self, new_status):
        self.status = new_status

    def get_service_message_data(self):
        """
        Returns the attribute names and values in dictionary form for use by the message wrapper (GOOutputInterface).
        """
        service_message_data = {
            "service_name": self.service_name,
            "group_id": self.group_id,
            "service_type": self.service_type,
            "interval_start": self.interval_start,
            "interval_duration": self.interval_duration,
            "power": self.power,
            "ramp": self.ramp,
            "price": self.price
        }
        return service_message_data

# ------------------------------------------------Function Definitions------------------------------------------------


def instantiate_callback_classes(simulation_id, gapps_object, edmCore):
    """
    Instantiates the callback classes.
    """
    global edmMeasurementProcessor
    edmMeasurementProcessor = EDMMeasurementProcessor()
    edmCore.gapps_session.subscribe(t.simulation_output_topic(edmCore.sim_mrid), edmMeasurementProcessor)
    global edmTimekeeper
    edmTimekeeper = EDMTimeKeeper(edmCore)
    edmCore.gapps_session.subscribe(t.simulation_log_topic(edmCore.sim_mrid), edmTimekeeper)


# ------------------------------------------Program Execution (Main loop)------------------------------------------
def _main():
    """
    Main operating loop. Instantiates the core, runs the startup process, gets the sim mrid, instantiates the callback
    classes, and starts running the simulation. All ongoing processes are handled (and called) by the callback objects.
    Otherwise, sleeps until the end_program flag is thrown.
    """
    global mcConfiguration
    mcConfiguration = MCConfiguration()
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
