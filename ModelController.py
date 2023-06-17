
import os
import ast
import csv
import time
# import json
import xmltodict
import subprocess
import pandas as pd
from dict2xml import dict2xml
from pprint import pprint as pp
from gridappsd import topics as t
import xml.etree.ElementTree as ET
from gridappsd.simulation import Simulation
from gridappsd import GridAPPSD, DifferenceBuilder
"""
model controller
"""
import ast
import csv
import os
import sys
import pandas as pd
from gridappsd import GridAPPSD, DifferenceBuilder
from gridappsd import topics as t
from gridappsd.simulation import Simulation
import time
import xml.etree.ElementTree as ET
import xmltodict
from dict2xml import dict2xml
from datetime import datetime

end_program = False

# ------------------------------------------------ Class Definitions ------------------------------------------------


class MCConfiguration:
    """
    Provides user configurability of the MC when appropriate. Not to be confused with the GridAPPS-D configuration
    process, this provides global configuration for the MC as a whole. DER-S configuration should be handled within
    the DER-S Class definition, and not here.
    """
    def __init__(self):
        """
        ATTRIBUTES:

            .mc_file_directory: The root folder where the ME is located.

            .config_file_path: The text file containing the GridAPPS-D configuration info.

            .ders_obj_list: A dictionary containing the DER-S classes and objects *that will be used in the current
                simulation*. Add or comment out as appropriate for new DER-Ss or for different tests.

            .go_sensor_decision_making_manual_override: Set to True to use manual GOSensor decision making (That is,
                grid services are called by a text file rather than based on grid conditions.
                NOTE: Automatic mode is not currently implemented, so this should ALWAYS be set to True.

            .manual_service_filename: the .xml filename of the GOSensor manual service input file. Should be in MC root.

            .output_log_name: The name and location of the output logs. Rename before simulation with date/time, for example.
        """
        self.mc_file_directory = r"/home/seanjkeene/PycharmProjects/doe-egot-me/"
        self.config_file_path = self.mc_file_directory + r"Configuration/Config.txt"
        self.ders_obj_list = {
            'DERSHistoricalDataInput': 'dersHistoricalDataInput',
            'RWHDERS': 'rwhDERS'
            # ,
            # 'EXAMPLEDERClassName': 'exampleDERObjectName'
        }
        self.go_sensor_decision_making_manual_override = True
        self.manual_service_filename = "manually_posted_service_input.xml"
        self.output_log_name = 'Logged Grid State Data/MeasOutputLogs_' + datetime.today().strftime("%d_%m_%Y_%H_%M") + '.csv'


class EDMCore:
    """
    Provides central core functionality to the MC. Responsible for the startup process and storing the GridAPPS-D
    connection and simulation mRIDs and objects.
    """
    def __init__(self):
        self.mc_file_directory = os.getcwd()
        self.config_file_path = f"{self.mc_file_directory}/Configuration/simulation_configuration.json"
        # midrar is not using the WH emulators. So remove the RWHDERS and its respective key.
        self.ders_obj_list = {
            'DERSHistoricalDataInput': 'dersHistoricalDataInput'
        }
        self.go_sensor_decision_making_manual_override = False
        self.manual_service_filename = "manually_posted_service_input.xml"
        self.output_log_name = 'Logged_Grid_State_Data/MeasOutputLogs'
        self.gapps_session = None
        self.sim_session = None
        self.sim_start_time = None
        self.sim_current_time = None
        self.sim_mrid = None
        self.line_mrid = None
        self.config_parameters = None
        self.mrid_name_lookup_table = []
        self.cim_measurement_dict = []
        self.is_in_test_mode = False

    def get_sim_start_time(self):
        """
        ACCESSOR METHOD: returns the simulation start time (per the configuration file, not realtime)
        """
        return self.sim_start_time

    def get_line_mrid(self):
        """
        ACCESSOR METHOD: Returns the mRID for the current model (I.E. the IEEE 13-node test feeder).
        """
        return self.line_mrid

    def sim_start_up_process(self):
        """
        ENCAPSULATION METHOD: calls all methods required to set up the simulation process. Does not start the simulation
        itself, but performs the "startup checklist". This includes connecting to GridAPPS-D and the simulation, loading
        configuration from the file, instantiating all the (non-callback) objects, initializing DER-Ss, assigning
        DER-EMs and creating the association table, and connecting to the aggregator among others. See each method's
        docstring for more details.
        """
        self.connect_to_gridapps()
        self.load_config_from_file()
        self.initialize_line_mrid()
        self.establish_mrid_name_lookup_table()
        self.connect_to_simulation()
        self.initialize_sim_start_time()
        self.initialize_sim_time_step()
        self.initialize_sim_mrid()
        self.create_objects()
        self.initialize_all_der_s()
        derAssignmentHandler.create_assignment_lookup_table()
        derAssignmentHandler.assign_all_ders()
        derIdentificationManager.initialize_association_lookup_table()
        mcOutputLog.set_log_name()
        goSensor.load_manual_service_file()

    def load_config_from_file(self):
        """
        Loads the GridAPPS-D configuration string from a file and places the parameters in a variable for later use.
        """
        goTopologyProcessor.import_topology_from_file()
        goSensor.load_manual_service_file()


    def load_config_from_file(self):

        with open(mcConfiguration.config_file_path) as f:
            config_string = f.read()
            self.config_parameters = ast.literal_eval(config_string)

    def connect_to_gridapps(self):

        os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
        os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
        os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
        os.environ['GRIDAPPSD_PORT'] = '61613'

        # Connect to GridAPPS-D Platform
        self.gapps_session = GridAPPSD()
        assert self.gapps_session.connected

    def initialize_sim_mrid(self):

        self.sim_mrid = self.sim_session.simulation_id

    def initialize_line_mrid(self):

        self.line_mrid = self.config_parameters["power_system_config"]["Line_name"]
        return self.line_mrid

    def initialize_sim_start_time(self):

        self.sim_start_time = self.config_parameters["simulation_config"]["start_time"]
        return self.sim_start_time

    def initialize_sim_time_step(self):

        self.sim_time_step = self.config_parameters["simulation_config"]["duration"]
        return self.sim_time_step

    def connect_to_simulation(self):

        self.sim_session = Simulation(self.gapps_session, self.config_parameters)


    def create_objects(self):
        """
        Instantiates all non-callback classes. All objects are global to simplify arguments and facilitate decoupling.
        (Note: EDMCore is manually instantiated first, in the main loop function. This is part of the startup process.
        The callback classes need to be instantiated separately to ensure the callback methods work properly.)
        """
        global mcOutputLog
        mcOutputLog = MCOutputLog()
        global mcInputInterface
        mcInputInterface = MCInputInterface()
        global dersHistoricalDataInput
        dersHistoricalDataInput = DERSHistoricalDataInput(mcConfiguration)
        global rwhDERS
        rwhDERS = RWHDERS(mcConfiguration)
        global derAssignmentHandler
        derAssignmentHandler = DERAssignmentHandler()
        global derIdentificationManager
        derIdentificationManager = DERIdentificationManager()
        global goTopologyProcessor
        goTopologyProcessor= GOTopologyProcessor ()
        global goSensor
        goSensor = GOSensor()
        global goOutputInterface
        goOutputInterface = GOOutputInterface()

    def initialize_all_der_s(self):
        """
        Calls the initialize_der_s() method for each DER-S listed in mcConfiguration.ders_obj_list.
        """
        for key, value in mcConfiguration.ders_obj_list.items():
            eval(value).initialize_der_s()

    def start_simulation(self):
        """
        Performs one final initialization of the simulation start time (fixes a bug related to our use of the logging
        API tricking the timekeeper into thinking it's later than it is) and calls the method to start the actual
        simulation.
        """
        self.initialize_sim_start_time()
        self.sim_session.start_simulation()

    def start_simulation_and_pause(self):
        """
        Performs one final initialization of the simulation start time (fixes a bug related to our use of the logging
        API tricking the timekeeper into thinking it's later than it is) and calls the method to start the actual
        simulation. Then, immediately pauses the simulation. This allows test harnesses to test a fully set up
        simulation without necessarily requiring the entire simulation process to run.
        """
        self.initialize_sim_start_time()
        self.sim_session.start_simulation()
        self.sim_session.pause()

    def establish_mrid_name_lookup_table(self):
        """
        This currently creates two lookup dictionaries. mrid_name_lookup_table gets the real names of measurements for
        the measurement processor/logger. cim_measurement_dict gives a more fully fleshed out dictionary containing
        several parameters related to measurements that are appended to the measurement processor's current readings.
        """
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
            'parameters': {'model_id': edmCore.initialize_line_mrid()}
        }

        cim_dict = edmCore.gapps_session.get_response(config_api_topic, message, timeout=20)
        measdict = cim_dict['data']['feeders'][0]['measurements']
        self.cim_measurement_dict = measdict
    def get_mrid_name_lookup_table(self):
        """
        ACCESSOR METHOD: Returns the mrid_name_lookup_table.
        """
        return self.mrid_name_lookup_table

    def get_cim_measurement_dict(self):
        """
        ACCESSOR METHOD: Returns the cim_measurement.dict.
        """
        return self.cim_measurement_dict

    def put_in_test_mode(self):
        self.is_in_test_mode = True


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
            mcOutputLog.close_out_logs()
            global end_program
            end_program = True

        def update_and_increment_timestep(log_message, self):
            """
            Increments the timestep only if "incrementing to " is within the log_message; otherwise does nothing.
            """
            if "incrementing to " in log_message:
                if log_message != self.previous_log_message:  # Msgs get spit out twice for some reason. Only reads one.
                    self.increment_sim_current_time()
                    print("\nCurrent timestep:\t" + self.sim_current_time)
                    self.perform_all_on_timestep_updates()
                    self.previous_log_message = log_message
                    if edmCore.is_in_test_mode is True:
                        print("PAUSING SIMULATION FOR TESTING")
                        edmCore.sim_session.stop()

                        # for i in rwhDERS.input_identification_dict:
                        #     print(rwhDERS.input_identification_dict[i]['Filepath'])

                        # print(rwhDERS.input_identification_dict[list(rwhDERS.input_identification_dict.keys())[0]]['Filepath'])
                        global end_program
                        end_program = True

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
        print("Performing on-timestep updates:")
        self.edmCoreObj.sim_current_time = self.sim_current_time
        mcInputInterface.update_all_der_s_status()
        mcInputInterface.update_all_der_em_status()
        # goSensor.update_sensor_states()
        mcOutputLog.update_logs()
        goSensor.make_service_request_decision()
        goOutputInterface.get_all_posted_service_requests()
        goOutputInterface.send_service_request_messages()


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
        self.measurement_mrids = self.current_measurements.keys()

        for i in self.measurement_mrids:
            try:
                lookup_mrid = next(item for item in self.mrid_name_lookup_table if item['measid'] == i)

            except StopIteration:
                print(f"\n\n-------- lookup_mrid --------")
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
                self.current_measurements[key]['MeasType'] = measurement_table_dict_containing_mrid['measurementType']
            except StopIteration:
                print("\n\n ---------- Measurements updated with amplifying information ---------- \n\n")

    def append_association_data(self):
        """
        Appends association data.
        """
        self.assignment_lookup_table = derAssignmentHandler.get_assignment_lookup_table()
        for item in self.assignment_lookup_table:

            original_name = item['Name']
            formatted_name = original_name
            item['DER-EM Name'] = formatted_name

        for key, value in self.current_measurements.items():

            try:
                assignment_dict_with_given_name = next(item for item in self.assignment_lookup_table if
                                                       item['DER-EM Name'] == self.current_measurements[key][
                                                           'Conducting Equipment Name'])
                self.current_measurements[key]['Inverter Control mRID'] = assignment_dict_with_given_name['mRID']
                input_name = derIdentificationManager.get_meas_name(assignment_dict_with_given_name['mRID'])
                self.current_measurements[key]['Input Unique ID'] = input_name
            except StopIteration:
                pass


class RWHDERS:
    """
    The Resistive Water Heater DER-S. This DER-S is designed to build on prior work by the Portland State Univerity
    Power Engineering Group. RWHDERS is designed to provide a means for resistive water heaters to be modeled and
    simulated in the Modeling Environment.

    The input to RWHDERS is information from water heater emulators that are/will be provided by the GSP (via the EGoT
    server/client system). These emulators function over time as a resistive water heater, turning on and off based on
    current tank temperature, ambient losses, usage profiles, etc. These functions are handled externally to the ME,
    however: the end result is a series of .csv files contained in the RWHDERS Inputs folder.

    The ME uses these .csv files as follows. Each file is named "DER#####_Bus###.csv". The first set of numbers is a
    serial number used as each emulated DER input's 'unique identifier'. The second set is the 'locational information',
    in this case the Bus the DER should be located on in the model. The contents of the .csv file are a single pair of
    values: "P", for power, and a number corresponding to what the power should be set to. This is by agreement with
    the GSP designer; in the future, the file could contain voltages, or more complex information such as usage profiles
    that would require modification to the RWHDERS class to parse.

    At the beginning of each simulation, the DERAssignmentHandler class calls the assign_der_s_to_der_em() function for
    each DER-S, including RWHDERS. This function associates each unique identifier with the mRID of a DER-EM. These
    DER-EMs already exist in the model and do nothing unless associated with a DER-S unit.

    During the simulation, each time step RWHDERS reads the .csv files for updates. The power levels for each DER are
    processed into a standard message format used by MCInputInterface. The association data is used to ensure each
    input is being sent to the proper DER-EM by MCInputInterface. Then, again on each timestep, MCInputInterface updates
    the DER-EMs in the model with the new power data, which is reflected in the logs.

    In this way, changes to water heater states are converted to time-valued power changes, which are sent to RWHDERS,
    processed by the MC, and written into the simulation so that grid states reflect the changes.

    ATTRIBUTES:
        .der_em_input_request: Contains the new DER-EM states for this timestep, already parsed and put into list
            format by RWHDERS. The list is so multiple DER-EMs can be updated per timestep.

        .input_file_path: The folder in which the RWHDERS input files are located.

        .input_identification_dict: a dictionary of identification information for each DER input. The keys are the
           serial numbers parsed from each file name, and the values include the buses and the filename. Used during
           assignment, and also on time step to get the right data from the right file for each DER's unique ID.
    """
    def __init__(self, mcConfiguration):
        self.der_em_input_request = []
        self.input_file_path = mcConfiguration.mc_file_directory + r"/RWHDERS Inputs/"
        self.input_identification_dict = {}

    def initialize_der_s(self):
        """
        This function (with this specific name) is required in each DER-S used by the ME. The EDMCore's initialization
        process calls this function for each DER-S activated in MCConfig to perform initialization tasks. This does not
        include DER-EM assignment (see assign_der_s_to_der_em). In this case, all this function does is call
        the parse_input_file_names_for_assignment() function. See below.
        """
        self.parse_input_file_names_for_assignment()

    def assign_der_s_to_der_em(self):
        """
        This function (with this specific name) is required in each DER-S used by the ME. The DERAssignmentHandler
        calls this function for each DER-S activated in MCConfig. This function's purpose is to take unique identifiers
        from each "DER input" for a given DER-S and "associate" them with the mRIDs for DER-EMs in the model. This is
        done using locational data: I.E. a specific DER input should be associated with the mRID of a DER-EM on a given
        bus. This function does those tasks using the input_identification_dict generated in the initialization process
        (see self.parse_input_file_names_for_assignment())
        """
        # print('iid')
        # print(self.input_identification_dict)
        for key, value in self.input_identification_dict.items():
            der_id = key
            der_bus = value['Bus']
            der_mrid = derAssignmentHandler.get_mRID_for_der_on_bus(der_bus)
            der_being_assigned = {der_id: der_mrid}
            derAssignmentHandler.append_new_values_to_association_table(der_being_assigned)

    def parse_input_file_names_for_assignment(self):
        """
        This function is called during the DER-S initialization process. It reads all the files in the RWHDERS Inputs
        folder and parses them into an input dictionary containing the unique ID, file name, and Bus location for each.
        These are used during assignment and each time step to "connect the dots" between the input file and the
        DER-EM which represents its data.
        """
        filename_list = os.listdir(self.input_file_path)
        parsed_filename_list = []
        for i in filename_list:
            g = i.split('_')
            g[0] = g[0][-5:]
            g[1] = g[1][3:6]
            parsed_filename_list.append({g[0]: {"Filepath": i, "Bus": g[1]}})
        for item in parsed_filename_list:
            self.input_identification_dict.update(item)

    def update_der_em_input_request(self):
        """
        Reads the input data from each file in the input identification dict, and puts it in a list readable by the
        MCInputInterface.
        """
        self.der_em_input_request.clear()
        for key, value in self.input_identification_dict.items():
            with open(self.input_file_path + value['Filepath'], newline='') as csvfile:
                der_input_reader = csv.reader(csvfile)
                for row in der_input_reader:
                    current_der_input = {row[0]: row[1]}
                    # print(current_der_input)
            current_der_real_power = current_der_input['P']
            current_der_input_request = {key: current_der_real_power}
            self.der_em_input_request.append(current_der_input_request)



    def get_input_request(self):
        """
        This function (with this specific name) is required in each DER-S used by the ME. Accessor function that calls
        for an updated input request, then returns the updated request for use by the MCInputInterface
        """
        self.update_der_em_input_request()
        return self.der_em_input_request


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
        self.der_em_input_request = []
        if DERSHDIPath_test is None:
            self.historical_data_file_path = mcConfiguration.mc_file_directory + r"DERSHistoricalData Inputs/thesisfiginput.csv"
        else:
            self.historical_data_file_path = mcConfiguration.mc_file_directory + DERSHDIPath_test

        self.input_table = None
        self.list_of_ders = []
        self.location_lookup_dictionary = {}
        self.test_first_row = None
        self.new_values_inserted = False

    def initialize_der_s(self):
        """
        This function (with this specific name) is required in each DER-S used by the ME. The EDMCore's initialization
        process calls this function for each DER-S activated in MCConfig to perform initialization tasks. This does not
        include DER-EM assignment (see assign_der_s_to_der_em). In this case, all this function does is call
        the read_input_file() function. See below.
        """
        self.read_input_file()

    def get_input_request(self):
        """
        This function (with this specific name) is required in each DER-S used by the ME. Accessor function that calls
        for an updated input request, then returns the updated request for use by the MCInputInterface
        """
        self.update_der_em_input_request()
        # print("DER EM INPUT REQUEST")
        # print(self.der_em_input_request)
        return self.der_em_input_request

    def assign_der_s_to_der_em(self):
        """
        This function (with this specific name) is required in each DER-S used by the ME. The DERAssignmentHandler
        calls this function for each DER-S activated in MCConfig. This function's purpose is to take unique identifiers
        from each "DER input" for a given DER-S and "associate" them with the mRIDs for DER-EMs in the model. This is
        done using locational data: I.E. a specific DER input should be associated with the mRID of a DER-EM on a given
        bus.

        Updates:

        - The input_table[0] variable prints all der_loc and der_mag values for a single timestep.

        - [(location_lookup_dictionary[i])] returns a dictionary that looks like:
            {'DER0_loc':'DER0_mag',
            'DER1_loc':'DER1_mag',
            }
        and so forth.

        - In previous versions, der_being_assigned[i] returns the bus location, which is 632
        """

        for i in self.list_of_ders:
            der_being_assigned = {}
            der_being_assigned[i] = self.input_table[0][(self.location_lookup_dictionary[i])]

            der_being_assigned[i] = derAssignmentHandler.get_mRID_for_der_on_bus(der_being_assigned[i])
            assigned_der = dict([(value, key) for value, key in der_being_assigned.items()])
            derAssignmentHandler.append_new_values_to_association_table(assigned_der)

    def open_input_file(self):
        """
        Opens the historical data input file, read it as a .csv file, and parses it into a list of dicts.
        """

        """
        Update:
        The new method is the same as the old one. However, since we have 960 DERs in the feeder, and each DER has its own, dedicated Watts profile,
        we perform the following steps to parse each profile into a list of dictionaries:

            - Only read the profiles within the DERSHistoricalDataInput that start with the word (ders)
            - Sort the DERs profiles based on their order (from 1 - 960).
            - Append the bus, the DER magnitude, and Time to the dicionary (x). <-- same as the previous version of this function!
        """
        x = []

        ders_files = [file for file in os.listdir(self.historical_data_file_path) if file.startswith("ders")]
        ders_files_sorted = sorted(ders_files, key=lambda x: int(x.split("_")[1].split(".")[0]))

        for file in ders_files_sorted:
            df = pd.read_csv(self.historical_data_file_path+file)
            for index, row in df.iterrows():
                row = dict(row)
                x.append(row)

        return x


    def read_input_file(self):

        """
        Reads and parses the input file. Places all the input information in input_table. Also, parses the
        .csv file to determine the names and locations of each DER: when the timestamp column is removed, odd column
        headers are names and even headers are their associated locations. These lists are converted to a list
        of dictionaries to be passed to the assignment handler (which takes the locations for each DER name and assigns
        a DER-EM mRID at the proper location to the name, this allows the MC to provide updated DER states to the DER-EM
        without requiring the inputs to know DER-EM mRIDs.)
        """
        self.input_table = self.open_input_file()
        print("Retrieving locational data:")
        first_row = next(item for item in self.input_table)
        first_row = dict(first_row)
        first_row.pop('Time')
        print("First row:")
        print(first_row)
        self.test_first_row = first_row
        log_der_keys = list(first_row.keys())
        # print(log_der_keys)
        for i in range(len(log_der_keys)):
            if i % 2 == 0:
                der_name = log_der_keys[i]
            else:
                der_loc = log_der_keys[i]
                self.location_lookup_dictionary[der_name] = der_loc
                # print("Current dict:")
                # print(self.location_lookup_dictionary)
        self.list_of_ders = list(self.location_lookup_dictionary.keys())
        # print("List of DERS:")
        # print(self.list_of_ders)

    def update_der_em_input_request(self, force_first_row=False):
        """
        Checks the current simulation time against the input table. If a new input exists for the current timestep,
        it is read, converted into an input dictionary, and put in the current der_input_request
        (see MCInputInterface.get_all_der_s_input_requests() )

        Update:

        new_values_listed flag is used for Grid Services. Every time DER-EMs have new inputs, it means the grid
        states will be updated. Therefore, we need to check for a grid service.
        """
        self.der_em_input_request.clear()
        try:
            if force_first_row is True:
                print("DERHistoricalDataInput TEST MODE: retrieving first item from input log")
                input_at_time_now = next(item for item in self.input_table)
            else:
                input_at_time_now = next(item for item in self.input_table if int(edmCore.sim_current_time) <=
                                         int(item['Time']) < (int(edmCore.sim_current_time) + 1))
            self.new_values_inserted = True
            input_at_time_now = dict(input_at_time_now)
            input_at_time_now.pop('Time')
            for i in self.list_of_ders:
                self.der_em_input_request.append({i: input_at_time_now[i]})
        except StopIteration:
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
    mRID, so that its states can be updated in the model. Each DER-S DER unit requires a unique identifier (a name, a
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
        PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX c:  <http://iec.ch/TC57/CIM100#>
        SELECT ?name ?id ?bus ?ratedS ?ratedU ?ipu ?p ?q ?fdrid (group_concat(distinct ?phs;separator=\"\") as ?phases) WHERE {{
         ?s r:type c:BatteryUnit.
         ?s c:IdentifiedObject.name ?name.
          ?s c:IdentifiedObject.mRID ?id.
         ?pec c:PowerElectronicsConnection.PowerElectronicsUnit ?s.
        VALUES ?fdrid {{"{edmCore.line_mrid}"}}  # psu_feeder
         ?pec c:Equipment.EquipmentContainer ?fdr.
         ?fdr c:IdentifiedObject.mRID ?fdrid.
         ?pec c:PowerElectronicsConnection.ratedS ?ratedS.
         ?pec c:PowerElectronicsConnection.ratedU ?ratedU.
         ?pec c:PowerElectronicsConnection.maxIFault ?ipu.
         ?pec c:PowerElectronicsConnection.p ?p.
         ?pec c:PowerElectronicsConnection.q ?q.
         OPTIONAL {{?pecp c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?pec.
         ?pecp c:PowerElectronicsConnectionPhase.phase ?phsraw.
           bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) }}
         ?t c:Terminal.ConductingEquipment ?pec.
         ?t c:Terminal.ConnectivityNode ?cn.
         ?cn c:IdentifiedObject.name ?bus
        }}
        GROUP by ?name ?id ?bus ?ratedS ?ratedU ?ipu ?p ?q ?fdrid
        ORDER by ?name
        '''

    def get_assignment_lookup_table(self):
        """
        ACCESSOR: Returns the assignment lookup table. Used in the message appendage process.
        """
        return self.assignment_lookup_table

    def create_assignment_lookup_table(self):
        """
        Runs an extended SPARQL query on the database and parses it into the assignment lookup table: that is, the names
        and mRIDs of all DER-EMs on each bus in the current model.
        """
        der_em_mrid_per_bus_query_output = edmCore.gapps_session.query_data(self.der_em_mrid_per_bus_query_message)
        x = []
        for i in range(len(der_em_mrid_per_bus_query_output['data']['results']['bindings'])):
            x.append({'Name': der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['name']['value'],
                      'Bus': der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['bus']['value'],
                      'mRID': der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['id']['value']})
        self.assignment_lookup_table = x

    def assign_all_ders(self):
        """
        Calls the assignment process for each DER-S. Uses the DER-S list from MCConfiguration, so no additions are
        needed here if new DER-Ss are added.
        """
        self.assignment_table = self.assignment_lookup_table

        # Object list contains string names of objects. eval() lets us use these to call the methods for the proper obj
        for key, value in mcConfiguration.ders_obj_list.items():
            eval(value).assign_der_s_to_der_em()

        print("DER Assignment complete.")
        # print(self.association_table)

    def get_mRID_for_der_on_bus(self, Bus):
        """
        For a given Bus, checks if a DER-EM exists on that bus and is available for assignment. If so, returns its mRID
        and removes it from the list (so a DER-EM can't be assigned twice).
        """
        print("Getting mRID for a der on bus:")
        print(Bus)
        try:
            next_mrid_on_bus = next(item for item in self.assignment_table if item['Bus'] == str(Bus))
            mrid = next_mrid_on_bus['mRID']
            self.assignment_table = [i for i in self.assignment_table if not (i['mRID'] == mrid)]
        except StopIteration:
            print("FATAL ERROR: Attempting to assign a DER to a nonexistent DER-EM. "
                  "The bus may be wrong, or may not contain enough DER-EMs. Verify test.")
            quit()


        return mrid

    def append_new_values_to_association_table(self, values):
        """
        Used by DER-S classes to add new values to the association table during initialization.
        """
        self.association_table.append(values)



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
        self.test_tpme1_unified_input_request = []

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
        # print("online_ders")
        # print(online_ders)
        self.current_unified_input_request.clear()
        for key, value in mcConfiguration.ders_obj_list.items():
            # print(value)
            self.current_unified_input_request = self.current_unified_input_request + eval(value).get_input_request()
        print("Current unified input request:")
        print(self.current_unified_input_request)
        # For TP-ME1-DER01:
        if edmCore.sim_current_time == "1570041120":
            self.test_tpme1_unified_input_request = list(self.current_unified_input_request)


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
            der_name_to_look_up = der_name_to_look_up[0] # DER_mags
            associated_der_em_mrid = derIdentificationManager.get_der_em_mrid(der_name_to_look_up)
            my_diff_build.add_difference(associated_der_em_mrid,
                                         "PowerElectronicsConnection.p",
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
    class; the XML contains each "group" and whatever buses are members of it.

    UPDATE:

    Since grid services might be on a substation level, feeder level, transformer level, or segment level, this class
    extracts the branches of each level, which will be later used by other classes to post a Grid Service to the
    DERMS.

        - The PSU feeder topology is similar to the CSIP topology; it contains the following:
              --------------------------------------------
              name on feeder    |   reference name on CSIP
              --------------------------------------------
              SourceBus         |   Substation
              N6*               |   Group
              Meter*            |   Feeder
              OL*               |   Segment names
              xfmr*             |   transformers
              tlx*              |   DER Busses

        - The updated version of this class aligns with the older version objectives. It is however expanded to accommodate
        more complex topologies.
    """
    def __init__(self):

        self.topology_file = './Configuration/psu_feeder_topology.xml'
        # self.topology_file = './Configuration/archive/topology.xml'


    def import_topology_from_file(self):
        """
        Read topology file
        """
        tree = ET.parse(self.topology_file)
        root = tree.getroot()

        return root

    def get_substation(self):
        """
        Get the root name
        """
        return self.import_topology_from_file().tag

    def get_groups (self):
        """
        Get groups in root
        """
        group = self.get_elements(self.import_topology_from_file(), 'group', 'name')
        return group

    def get_feeders (self):
        """
        Get feeder in each group
        """
        feeders = self.get_elements(self.import_topology_from_file(), 'feeder', 'name')
        return feeders

    def get_segments (self):
        """
        Get segments in each feeder
        """
        segments = self.get_elements(self.import_topology_from_file(), 'segment', 'name')
        return segments

    def get_xfmrs (self):
        """
        Get transformers in each segment
        """
        xfmrs = self.get_elements(self.import_topology_from_file(), 'xfmr', 'name')
        return xfmrs

    def get_buses (self):
        """
        Get buses in each segment for each DER
        """
        buses = self.get_elements(self.import_topology_from_file(), 'bus', 'name')
        return buses

    def get_elements (self, element, tag, attribute):
        """
        Loop to retrieve the above attributes
        """
        attributes = []

        for elem in element.iter(tag):
            attributes.append(elem.get(attribute))
        return attributes


class GOSensor:
    """
    This class retrieves fully formatted grid states from the measurement processor, filters them down to necessary
    information, and makes determinations (automatically or manually) about grid services, whether they're required,
    happening satisfactorily, etc. These determinations are sent to the output API to be communicated to the DERMS.

    NOTE: In the current state of the ME, only Manual Mode is implemented. Automatic Mode requires development of GO
    threshold detection algorithms that, while more realistic, do not support the current goal of functionally testing
    a DERMS.

    Also, make sure the simulation time in the Configuration/Config.txt matches the start_time in the
    manually_posted_service_input.xml

    ATTRIBUTES:
        .current_sensor_states: Grid states read into the sensor. Automatic mode only. Not currently implemented.

        .service_request_decision: Determination whether a grid service is needed. Automatic mode. Not implemented.

        .posted_service_list: List of posted service objects. Used by both Automatic and Manual modes.

        .manual_service_xml_data: In Manual Mode, the data contained within the manual service xml file. To be parsed
            and posted service objects generated from this data.
    """
    def __init__(self):

        self.service_request_decision = None
        self.current_sensor_states = None
        self.manual_service_xml_data = {}
        self.voltage_support_buses = []
        self.posted_service_list = []

        # Set Feeder Parameters

        self.voltage_tolerance = 0.01     # 5% is the voltage tolerance as per ANSI C84.1

        # Set the external inverter files

        self.current_path = os.getcwd()
        self.inv_file_path = f'{self.current_path}/inverter_control_file/'
        self.inv_file_name = 'model_startup_test.glm'

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
            self.bus_list = self.setup_feeder_analysis_level()
            self.set_volt_var_thresholds()
            self.update_sensor_states()
        else:
            print("Service request failure. Wrong input.")

    def setup_feeder_analysis_level (self):
        """
        Uncomment the level of where Grid Services should be monitored. All services should be working on substation,
        segments, and feeders levels.
        """
        level_analysis = {
            "goTopologyProcessor": {
                # "self.segments_list": {
                #     "function": ".get_segments()",
                #     "threshold": 2401
                #     },
                # "self.feeders_list": {
                #     "function": ".get_feeders()",
                #     "threshold": 2401
                #     },
                # "self.groups_list": {
                #     "function": ".get_groups()",
                #     "threshold": 2401
                #     },
                "self.bus_list": {
                    "function": ".get_buses()",
                    "nominal_voltage": 120
                    }
                }
            }

        for key, value in level_analysis.items():
            for clas, func in value.items():
                self.feeder_nominal_voltage = func['nominal_voltage']
                return eval(f"{key}{func['function']}")

    def set_volt_var_thresholds (self):
        """
        Initially, sets the maximum and minimum thresholds for volt/var grid service.
        Upon completion, this function will set all grid services parameters thresholds (i.e peak demand, voltage support, etc).
        """
        self.max_threshold = self.feeder_nominal_voltage + (self.feeder_nominal_voltage * self.voltage_tolerance)
        self.min_threshold = self.feeder_nominal_voltage - (self.feeder_nominal_voltage * self.voltage_tolerance)

    def update_sensor_states(self):

        print("Checking for a Grid Service...")

        parsed_measurements = edmMeasurementProcessor.get_current_measurements()
        if parsed_measurements:
            print(dersHistoricalDataInput.new_values_inserted)
            try:
                for key, value in parsed_measurements.items():
                    self.detect_grid_service_type (value)
            except AttributeError:                              # eliminating the timestamp attribute
                pass

    def detect_grid_service_type (self, value):
        """
        Parse the measurements per timestep. If a voltage drop is detected or transformers are overloaded,
        other functions are called to respond to the detected drops. Services are posted only once unless
        a new input value is inserted to the simulation.

        NOTE: Once a service is needed, it is directly posted to DERMS. Voltage support, however, is an exception.
        All functions related to voltage service are outlined in initialize_volt_var_support_service() function.
        """

        if (value.get('MeasType') == "PNV" and
            value.get('Bus') in self.bus_list and
            dersHistoricalDataInput.new_values_inserted is True and
            (self.min_threshold > value.get('magnitude', float('inf')) or value.get('magnitude', float('-inf')) > self.max_threshold)
            ):

            self.initialize_volt_var_support_service(bus=value['Bus'],magnitude=value['magnitude'])


    def initialize_volt_var_support_service (self, bus, magnitude):
        """
        Since GridAPPS-D storage objects do not provide volt/var support, we use external GridLAB-D file that provides
        the needed VARs to adjust the voltage.
        """
        self.voltage_support_buses.append(bus)

        self.set_grid_service_type(grid_service_type='"Voltage service"')

        # self.setup_ext_inverter_startup_file ()
        # self.initialize_grid_Service_elements (bus, magnitude)
        # self.run_ext_inverter_startup_file ()


    def set_grid_service_type (self, grid_service_type):
        self.service_type = grid_service_type
        print(self.service_type)
        print(self.voltage_support_buses)
        dersHistoricalDataInput.new_values_inserted = False

    def load_manual_service_file(self):

        """
        MANUAL MODE: Reads the manually_posted_service_input.xml file during MC initialization and loads it into
        a dictionary for later use.
        """
        # input_file = open(mcConfiguration.manual_service_filename, "r") # manually_posted_service_input.xml
        # data = input_file.read()
        # input_file.close()
        # self.manual_service_xml_data = xmltodict.parse(data)
        input_file = mcConfiguration.manual_service_filename
        self.tree = ET.parse(input_file)


    def manually_post_service(self, sim_time):
        """
        Called by make_service_request_decision() when in MANUAL mode. Reads the contents of the manual service
        dictionary, draws all relevant data points for each service, and instantiates a GOPostedService object for each
        one, appending the objects to a list.
        """

        for key, item in self.manual_service_xml_data['services'].items():
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
                item.set_status(True)
            else:
                print("----------------All already posted----------------")


    def generate_service_messages(self):
        """
        Converts the current_service_requests list of dicts into a proper xml format. Used by the xml writed in
        send_service_request_messages().
        """
        request_out_xml = '<services>\n'
        service_serial_num = 1
        for item in self.current_service_requests:
            request_out_xml = request_out_xml + '<service' + str(service_serial_num) + '>\n'
            request_out_xml = request_out_xml + dict2xml(item) + '\n'
            request_out_xml = request_out_xml + '</service' + str(service_serial_num) + '>\n'
            service_serial_num = service_serial_num + 1
        request_out_xml = request_out_xml + '</services>'
        return request_out_xml

    def send_service_request_messages(self):
        """
        Writes the current service request messages to an xml file, which will be accessed by the GSP for its service
        provisioning functions.
        """
        xmlfile = open("output_to_DERMS/OutputtoGSP.xml", "w")
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

    Update:
        - The objectives of this class is the same as the old version. However, its functionality is different as mentioned below:
            - At this level of testing, we need more simulation time (up to 12 hrs). <-- Existing GridAPPS-D bugs do not allow for more than 12 hrs simulation.
            - More data stream is expected due to the long simulation time.

        - New functionalities;
            - The timestamp values are written at the same time as the measurements in each timestep. Therefore, append_timestamps() function is optimized.
            - More than one log file are now exported. Easier to parse, less time when reading each file in Python, and memory-convienient during and post simulation.
                - A Python parsing script is available in python_support folder as an example.
            - After several trials-and-errors, it was noted that exporting a log file after 100 timesteps is sufficient. (Depends on Computer features and OS)
            - message_size_checkpoint() is a function that monitors the simulation time steps, closing old files, openning new files,
            and updating needed class parameters.
    """

    def __init__(self):
        self.csv_file = None
        self.log_name = ''
        self.mrid_name_lookup_table = []
        self.header_mrids = []
        self.header_names = []
        self.csv_dict_writer = None
        self.current_measurement = None
        self.is_first_measurement = True
        self.message_size = 0
        self.file_num = 0



    def update_logs(self):
        """
        During the first measurement, performs housekeeping tasks like opening the file, setting the name, translating
        the header to something readable, and writing the header. On all subsequent measurements, it writes a row of
        measurements to the logs.

        Note: The first timestep in the logs will be several seconds after the actual simulation start time.

        UPDATE:
            - timestamp array is eliminated. Removed from the above paragraph!
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
            self.append_timestamps()
            self.write_row()
            self.message_size_checkpoint()


    def message_size_checkpoint (self):
        """
        Set the message size and checks if the it is exceeded. If it is, it closes the current file, opens a new file, and
        changes the is_first_measurement flag to True so we can head back to the update_logs function.

        NOTE: The message_size must be hardcoded for long Simulations.
        """
        self.message_size +=1
        # print('Current message size --->', self.message_size)
        if self.message_size > 50:
            print('Message size threshold reached!', self.message_size)
            print(f"Openning file ---> {mcConfiguration.output_log_name}_{self.file_num}.csv")
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
        self.csv_dict_writer = csv.DictWriter(self.csv_file, self.header_mrids) # header_mrids is a dict of object mrid and its name

    def close_out_logs(self):
        """
        Closes the log file and re-appends the timestamps.
        """
        self.csv_file.close()

    def translate_header_names(self):
        """
        Looks up the plain english names for the headers and provides them to a dictionary for use by write_header().
        """
        self.header_mrids = self.current_measurement.keys()
        for i in self.header_mrids:
            if i != 'Timestamp':
                try:
                    lookup_mrid = next(item for item in self.mrid_name_lookup_table if item['measid'] == i)
                except StopIteration:
                    print(lookup_mrid)
                lookup_name = lookup_mrid['name']
                self.header_names.append(lookup_name)

        self.header_mrids = dict(zip(list(self.header_mrids), self.header_names))
        self.header_mrids['Timestamp'] = 'Timestamp'

    def append_timestamps(self):
        """
        Convert simulation time to a human-readable format.
        """
        self.current_measurement['Timestamp'] = pd.to_datetime(edmTimekeeper.sim_current_time, unit='s')

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
        self.log_name = f"{mcConfiguration.output_log_name}_{self.file_num}.csv"
        self.file_num += 1


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
def set_testing_conditions():
    """
    Used for unit testing. Sets up the ME for a run without actually starting the simulation. This will allow most
    classes and specifications to be tested by importing ModelController.py as a module and using this method
    to set initial conditions.
    """
    global mcConfiguration
    mcConfiguration = MCConfiguration()
    global edmCore
    edmCore = EDMCore()  # EDMCore must be manually instantiated.
    edmCore.put_in_test_mode()
    edmCore.sim_start_up_process()
    edmCore.start_simulation_and_pause()
    edmCore.initialize_sim_mrid()
    instantiate_callback_classes(edmCore.sim_mrid, edmCore.gapps_session, edmCore)

def _main(test_mode = False, DERSHDI_FilePath = None):
    """
    Main operating loop. Instantiates the core, runs the startup process, gets the sim mrid, instantiates the callback
    classes, and starts running the simulation. All ongoing processes are handled (and called) by the callback objects.
    Otherwise, sleeps until the end_program flag is thrown.
    """
    global DERSHDIPath_test
    DERSHDIPath_test = DERSHDI_FilePath
    global mcConfiguration
    mcConfiguration = MCConfiguration()
    global edmCore
    edmCore = EDMCore()  # EDMCore must be manually instantiated.
    # test_mode = True
    if test_mode is True:
        edmCore.put_in_test_mode()
    edmCore.sim_start_up_process()
    edmCore.start_simulation()
    edmCore.initialize_sim_mrid()
    instantiate_callback_classes(edmCore.sim_mrid, edmCore.gapps_session, edmCore)

    global end_program
    end_program = False
    while not end_program:
        time.sleep(0.1)

    if end_program:
        print('Ending program.')
        quit()


if __name__ == "__main__":
    _main()
