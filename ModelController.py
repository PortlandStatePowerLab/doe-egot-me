"""
model controller
"""
import ast
import csv
import os
import traceback

import pandas as pd
from gridappsd import GridAPPSD, DifferenceBuilder
from gridappsd import topics as t
from gridappsd.simulation import Simulation
import time
import xml.etree.ElementTree as ET
import xmltodict
from dict2xml import dict2xml

end_program = False




# ------------------------------------------------ Class Definitions ------------------------------------------------

class MCConfiguration:
    """
    Provides user configurability of the MC when appropriate. Not to be confused with the GridAPPS-D configuration
    process.
    """
    def __init__(self):
        self.config_file_path = r"C:\Users\stant\PycharmProjects\doe-egot-me\Config.txt"
        self.ders_obj_list = {
            'DERSHistoricalDataInput' : 'dersHistoricalDataInput',
            'RWHDERS': 'rwhDERS'
            # ,
            # 'EXAMPLEDERClassName': 'exampleDERObjectName'
        }
        self.go_sensor_decision_making_manual_override = True
        self.manual_service_filename = "manually_posted_services.xml"

class EDMCore:
    """
    Provides core functionality to the MC. Responsible for the startup process and storing the GridAPPS-D connection
    and simulation mRIDs and objects.
    """
    gapps_session = None
    sim_session = None
    sim_start_time = None
    sim_current_time = None
    sim_mrid = None
    line_mrid = None
    config_parameters = None
    mrid_name_lookup_table = []
    cim_measurement_dict = []

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
        self.initialize_sim_mrid()
        self.create_objects()
        self.initialize_all_der_s()
        derAssignmentHandler.create_assignment_lookup_table()
        derAssignmentHandler.assign_all_ders()
        derIdentificationManager.initialize_association_lookup_table()
        mcOutputLog.set_log_name()
        goSensor.load_manual_service_file()
        # TODO: Connect to aggregator

    def load_config_from_file(self):
        """
        Loads the GridAPPS-D configuration string from a file and places the parameters in a variable for later use.
        """
        with open(mcConfiguration.config_file_path) as f:
            config_string = f.read()
            self.config_parameters = ast.literal_eval(config_string)

    def connect_to_gridapps(self):
        """
        Connects to GridAPPS-D and creates the gridapps session object.
        """
        self.gapps_session = GridAPPSD("('localhost', 61613)", username='system', password='manager')

    def initialize_sim_mrid(self):
        """
        Retrieves the simulation mRID from the simulation object. The mRID is used to connect to messaging topics,
        while the object contains methods to, for example, start the simulation.
        """
        self.sim_mrid = self.sim_session.simulation_id
        print(self.sim_mrid)

    def initialize_line_mrid(self):
        """
        Retrieves the model mRID from the config parameters.
        """
        self.line_mrid = self.config_parameters["power_system_config"]["Line_name"]

    def initialize_sim_start_time(self):
        """
        Retreives the simulation start time from the config parameters. Note: this is a setting, not the real current
        time.
        """
        self.sim_start_time = self.config_parameters["simulation_config"]["start_time"]
        print("Simulation start time is:")
        print(self.sim_start_time)

    def connect_to_simulation(self):
        """
        Connects to the GridAPPS-D simulation (rather than the overall program) and creates the simulation object.
        """
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
        dersHistoricalDataInput = DERSHistoricalDataInput()
        global rwhDERS
        rwhDERS = RWHDERS()
        global derAssignmentHandler
        derAssignmentHandler = DERAssignmentHandler()
        global derIdentificationManager
        derIdentificationManager = DERIdentificationManager()
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
            'parameters': {'model_id': edmCore.line_mrid}
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


class EDMTimeKeeper(object):
    """
    CALLBACK CLASS. GridAPPS-D provides logging messages to this callback class. on_message() filters these messages down
    to exclude everything except simulation timestep "incrementing to..." messages and simulation ending messages.
    Each time an incrementation message is received from GridAPPS-D, one second has elapsed. The Timekeeper increments
    the time each timestep; more importantly, it also calls all methods that are intended to run continuously during
    simulation runtime. perform_all_on_timestep_updates() updates the MC once per second, including receiving DER-S
    inputs, updating the DER-EMs, and updating the logs.

    Note: this does not include updating the grid state measurements. GridAPPS-D retrieves grid states for the
    measurement callbacks once every three seconds using a completely different communications pathway. As such,
    measurements and their processing are not handled by this class in any way.
    """

    def __init__(self, simulation_id, gapps_object, edmCoreObj):
        self._gapps = gapps_object
        self._simulation_id = simulation_id
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

        def end_program():
            """
            Ends the program (See below within on_message() )
            """
            mcOutputLog.close_out_logs()
            global end_program
            end_program = True

        def update_and_increment_timestep(log_message, self):
            """
            Increments the timestep only if "incrementing to " is within the log_message, otherwise does nothing.
            """
            if "incrementing to " in log_message:
                if log_message != self.previous_log_message:  # Msgs get spit out twice for some reason. Only reads one.
                    self.increment_sim_current_time()
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

    NOTE: the API for measurements and timekeeping are completely seperate. The MC as a whole is synchronized with the
    timekeeping class, but measurement processes are done seperately. This is why logs will have repeated values: the
    logs are part of the MC and thus update once per second, but the grid states going IN to the logs are only updated
    once per three seconds.

    TODO: Refactor association/name appendage methods. They're pretty jank.
    """

    def __init__(self, simulation_id, gapps_object):
        self._gapps = gapps_object
        self._simulation_id = simulation_id
        self.measurement_timestamp = None
        self.current_measurements = None
        self.current_processed_grid_states = None
        self.run_once_flag = False
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
        TODO: Refactor and rewrite this docstring.
        """
        self.mrid_name_lookup_table = edmCore.get_mrid_name_lookup_table()
        self.measurement_lookup_table = edmCore.get_cim_measurement_dict()
        self.measurement_mrids = self.current_measurements.keys()
        for i in self.measurement_mrids:
            try:
                lookup_mrid = next(item for item in self.mrid_name_lookup_table if item['measid'] == i)
            except StopIteration:
                print(lookup_mrid)
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
                print("Measurements updated with amplifying information.")

    def append_association_data(self):
        """
        Appends association data.
        TODO: Refactor/rewrite.
        """
        self.assignment_lookup_table = derAssignmentHandler.get_assignment_lookup_table()
        for item in self.assignment_lookup_table:
            original_name = item['Name']
            formatted_name = original_name[:-len('_Battery')]
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
                # print("Nothing Found")
                pass
        # print("Fully formatted current measurements:")
        # print(self.current_measurements)


class RWHDERS:
    der_em_input_request = []
    current_input_request = None
    current_der_states = None
    input_file_path = r"C:/Users/stant/PycharmProjects/doe-egot-me/RWHDERS Inputs/"
    input_identification_dict = {}

    def initialize_der_s(self):
        """

        """
        self.parse_input_file_names_for_assignment()


    def assign_der_s_to_der_em(self):
        print('iid')
        print(self.input_identification_dict)
        for key,value in self.input_identification_dict.items():
            der_id = key
            der_bus = value['Bus']
            der_mrid = derAssignmentHandler.get_mRID_for_der_on_bus(der_bus)
            der_being_assigned = {der_id:der_mrid}
            derAssignmentHandler.append_new_values_to_association_table(der_being_assigned)

    def parse_input_file_names_for_assignment(self):
        """

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


    def update_wh_states_from_emulator(self):
        """

        """


        pass

    def update_der_em_input_request(self):
        """

        """
        self.der_em_input_request.clear()
        for key, value in self.input_identification_dict.items():
            import csv
            with open(self.input_file_path + value['Filepath'], newline='') as csvfile:
                der_input_reader = csv.reader(csvfile)
                for row in der_input_reader:
                    current_der_input = {row[0]: row[1]}
                    print(current_der_input)
            current_der_real_power = current_der_input['P']
            current_der_input_request = {key: current_der_real_power}
            self.der_em_input_request.append(current_der_input_request)


    def get_input_request(self):
        """

        """
        self.update_der_em_input_request()
        return self.der_em_input_request


class DERSHistoricalDataInput:
    der_em_input_request = []
    historical_data_file_path = r"C:\Users\stant\PycharmProjects\doe-egot-me\2p_input2.csv"
    input_file_name = None
    input_table = None
    list_of_ders = []
    location_lookup_dictionary = {}

    def initialize_der_s(self):
        """
        ENCAPSULATION: Calls the read_input_file
        """
        self.read_input_file()

    def get_input_request(self):
        """

        """
        self.update_der_em_input_request()
        print("DER EM INPUT REQUEST")
        print(self.der_em_input_request)
        return self.der_em_input_request

    def assign_der_s_to_der_em(self):
        """
        Assignment process for this DER-S. See DERAssignmentHandler.assign_all_ders()
        """
        for i in self.list_of_ders:
            der_being_assigned = {}
            der_being_assigned[i] = self.input_table[0][(self.location_lookup_dictionary[i])]
            der_being_assigned[i] = derAssignmentHandler.get_mRID_for_der_on_bus(der_being_assigned[i])
            assigned_der = dict([(value, key) for value, key in der_being_assigned.items()])
            derAssignmentHandler.append_new_values_to_association_table(assigned_der)

    def open_input_file(self):
        """
        TODO: Refactor. This can be in the scope of read_input_file.

        """
        with open(self.historical_data_file_path) as csvfile:
            r = csv.DictReader(csvfile)
            x = []
            for row in r:
                row = dict(row)
                x.append(row)
        print("Historical data file opened")
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
        log_der_keys = list(first_row.keys())
        print(log_der_keys)
        for i in range(len(log_der_keys)):
            if i % 2 == 0:
                der_name = log_der_keys[i]
            else:
                der_loc = log_der_keys[i]
                self.location_lookup_dictionary[der_name] = der_loc
                print("Current dict:")
                print(self.location_lookup_dictionary)
        self.list_of_ders = list(self.location_lookup_dictionary.keys())
        print("List of DERS:")
        print(self.list_of_ders)

    def update_der_em_input_request(self):
        """
        Checks the current simulation time against the input table. If a new input exists for the current timestep,
        it is read, converted into an input dictionary, and put in the current der_input_request
        (see MCInputInterface.get_all_der_s_input_requests() )
        """
        self.der_em_input_request.clear()
        try:
            input_at_time_now = next(item for item in self.input_table if int(edmCore.sim_current_time) <=
                                     int(item['Time']) < (int(edmCore.sim_current_time) + 1))
            print("Updating DER-EMs from historical data.")
            input_at_time_now = dict(input_at_time_now)
            input_at_time_now.pop('Time')
            for i in self.list_of_ders:
                self.der_em_input_request.append({i: input_at_time_now[i]})
        except StopIteration:
            print("End of input data.")
            return


class DERIdentificationManager:
    """
    This class manages the input association lookup table generated by the DERSAssignmentHandler. The accessor methods
    allow input unique IDs to be looked up for a given DER-EM mRID, or vice versa.
    """
    association_lookup_table = None

    def get_meas_name(self, mrid):
        """
        Returns a unique identifier for a given DER-EM mRID. If none found, the DER-EM was never assigned, and
        'Unassigned' is returned instead.
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
        Returns the associated DER-EM control mRID for a given input unique identifier. Unlike get_meas_name(), if none
        is found that signifies a critical error with the DERSAssignmentHandler.
        """
        x = next(d for i, d in enumerate(self.association_lookup_table) if name in d)
        return x[name]

    def initialize_association_lookup_table(self):
        """
        Gets the association table from the assignment handler.
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
    """
    der_em_assignment_list = None
    assignment_lookup_table = None
    assignment_table = None
    association_table = []
    location_data = None
    ders_in_use = None
    # TODO: See if you can do something about this query
    der_em_mrid_per_bus_query_message = """ 
    PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX c:  <http://iec.ch/TC57/CIM100#>
    SELECT ?name ?id ?bus ?ratedS ?ratedU ?ipu ?p ?q ?fdrid (group_concat(distinct ?phs;separator="\\n") as ?phases) WHERE {
     ?s r:type c:BatteryUnit.
     ?s c:IdentifiedObject.name ?name.
      ?s c:IdentifiedObject.mRID ?id.
     ?pec c:PowerElectronicsConnection.PowerElectronicsUnit ?s.
    # feeder selection options - if all commented out, query matches all feeders
    #VALUES ?fdrid {"_C1C3E687-6FFD-C753-582B-632A27E28507"}  # 123 bus
    VALUES ?fdrid {"_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62"}  # 13 bus
     ?pec c:Equipment.EquipmentContainer ?fdr.
     ?fdr c:IdentifiedObject.mRID ?fdrid.
     ?pec c:PowerElectronicsConnection.ratedS ?ratedS.
     ?pec c:PowerElectronicsConnection.ratedU ?ratedU.
     ?pec c:PowerElectronicsConnection.maxIFault ?ipu.
     ?pec c:PowerElectronicsConnection.p ?p.
     ?pec c:PowerElectronicsConnection.q ?q.
     OPTIONAL {?pecp c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?pec.
     ?pecp c:PowerElectronicsConnectionPhase.phase ?phsraw.
       bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) }
     ?t c:Terminal.ConductingEquipment ?pec.
     ?t c:Terminal.ConnectivityNode ?cn.
     ?cn c:IdentifiedObject.name ?bus
    }
    GROUP by ?name ?id ?bus ?ratedS ?ratedU ?ipu ?p ?q ?fdrid
    ORDER by ?name
    """

    def get_assignment_lookup_table(self):
        """
        ACCESSOR: Returns the assignment lookup table. Used in the message appendage process.
        """
        return self.assignment_lookup_table

    def create_assignment_lookup_table(self):
        """
        Runs an extended SPARQL query on the database and parses it into the assignment lookup table: that is, the names
        and mRIDs of all DER-EMs on each bus.
        """
        der_em_mrid_per_bus_query_output = edmCore.gapps_session.query_data(self.der_em_mrid_per_bus_query_message)
        # print("Bus query results:")
        # print(der_em_mrid_per_bus_query_output)
        x = []
        for i in range(len(der_em_mrid_per_bus_query_output['data']['results']['bindings'])):
            x.append({'Name': der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['name']['value'],
                      'Bus': der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['bus']['value'],
                      'mRID': der_em_mrid_per_bus_query_output['data']['results']['bindings'][i]['id']['value']})
        self.assignment_lookup_table = x
        print("TEST")
        print(self.assignment_lookup_table)

    def assign_all_ders(self):
        """
        Calls the assignment process for each DER-S. New DER-Ss should be added here as they're implemented.
        """
        self.assignment_table = self.assignment_lookup_table

        # Object list contains string names of objects. eval() lets us use these to call the methods for the proper obj
        for key, value in mcConfiguration.ders_obj_list.items():
            eval(value).assign_der_s_to_der_em()

        print("DER Assignment complete.")
        print(self.association_table)

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
            print("FATAL ERROR: Attempting to assign a DER to a nonexistant DER-EM. "
                  "The bus may be wrong, or may not contain enough DER-EMs. Verify test.")
            quit()
        print(next_mrid_on_bus)
        return mrid

    def append_new_values_to_association_table(self, values):
        self.association_table.append(values)


class MCInputInterface:
    """
    TODO: Refactor and add more functionality. Currently using a lot of vestigal test functions.
    TODO: Format methods in a way that makes this extensible when we move beyond simple power inputs.
    Input interface. Receives input messages from DER-Ss, retrieves the proper DER-EM input mRIDs for each input from
    the Identification Manager, and delivers input messages to the EDM that update the DER-EMs with the new states.
    """
    current_unified_input_request = []
    active_der_s_list = None
    test_DER_1_mrid = '_B1C7AD50-5726-4442-BA61-B8FA87C8E947'
    test_DER_2_mrid = '_2750969C-CBD5-41F4-BDCE-19287FBDCA71'
    test_DER_3_mrid = '_1720E0C8-A0CA-41BF-84DE-9847A17EBE26'

    def update_all_der_em_status(self):
        """
        TODO: I think this is the same thing as send_der_em_updates_to_edm?
        Currently, calls the test_der_em() method. In future, will call all input methods.
        """
        self.test_der_em()
        pass

    def update_all_der_s_status(self):
        """
        Gets the DER-S input requests. TODO: Refactor
        """
        self.get_all_der_s_input_requests()

    def get_all_der_s_input_requests(self):
        """
        TODO: Refactor
        Retrieves input requests from all DER-Ss and appends them to a unified input request.
        """
        online_ders = mcConfiguration.ders_obj_list
        print("online_ders")
        print(online_ders)
        self.current_unified_input_request.clear()
        for key, value in mcConfiguration.ders_obj_list.items():
            print(value)
            self.current_unified_input_request = self.current_unified_input_request + eval(value).get_input_request()
        print("Current unified input request:")
        print(self.current_unified_input_request)

    def send_der_em_updates_to_edm(self):
        """
        TODO: Refactor
        """
        pass

    def test_der_em(self):
        """
        Reads each line in the unified input request and uses the GridAPPS-D library to generate EDM input messages for
        each one. The end result is the inputs are sent to the associated DER-EMs and the grid model is updated with
        the new DER states. This will be reflected in future measurements.
        """
        input_topic = t.simulation_input_topic(edmCore.sim_mrid)
        for i in self.current_unified_input_request:
            der_name_to_look_up = list(i.keys())
            der_name_to_look_up = der_name_to_look_up[0]
            # print("DER Name to look up:")
            # print(der_name_to_look_up)
            associated_der_em_mrid = derIdentificationManager.get_der_em_mrid(der_name_to_look_up)
            # print("Associated DER EM mrid")
            # print(associated_der_em_mrid)
            # print(i[der_name_to_look_up])
            my_diff_build = DifferenceBuilder(edmCore.sim_mrid)
            my_diff_build.add_difference(associated_der_em_mrid, "PowerElectronicsConnection.p",
                                         int(i[der_name_to_look_up]), 0)
            message = my_diff_build.get_message()
            # print(message)
            edmCore.gapps_session.send(input_topic, message)
        self.current_unified_input_request.clear()


class GOTopologyProcessor:
    """
    'Topology' refers to where things are on the grid in relation to one another. In its simplest form, topology can
    refer to what bus each DER-EM is on. However, GOs and GSPs may view topology in more complex forms, combining
    buses into branches, groups, etc. More complex topologies are stored in xml files and read into the MC by this
    class; the XLM contains each "group" and whatever buses are members of it. This class will then be able to
    associate groups with buses as needed for the GO outputs, logging, etc.
    """
    topology_file_path = None
    topology_dict = {}
    inverse_topology_lookup_dict = {}
    bus_list = []
    group_list = []

    def import_topology_from_file(self):
        """
        Reads the topology xml file. This needs to be generated prior to the simulation and will be used by both the
        ME and the DERMS in use (ex. the GSP).

        TODO: Refactor.
        """
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
            bus_list = [x for item in bus_list for x in item]

        bus_list_final = []
        [bus_list_final.append(x) for x in bus_list if x not in bus_list_final]
        self.bus_list = bus_list
        # print(bus_list_final)

    # def parse_topology(self):
    #     pass

    def reverse_topology_dict(self):
        """
        I honestly don't remember what this is for.
        TODO: Remove if necessary.
        """
        pass

    def get_group_members(self, group_input):
        """
        Returns all buses contained in a given group.
        :param group_input:
        """
        for i in self.topology_dict:
            try:
                bus_return = i[group_input]
                bus_return = [x for item in bus_return for x in item]
                # print(bus_return)
            except KeyError:
                pass

    def get_groups_bus_is_in(self):
        """
        Returns all groups a given bus is a member of.
        """
        pass


class GOSensor:
    """
    NOT YET IMPLEMENTED.
    This class retrieves fully formatted grid states from the measurement processor, filters them down to necessary
    information, and makes determinations (automatically or manually) about grid services, whether they're required,
    happening satisfactorily, etc. These determinations are sent to the output API to be communicated to the DERMS.
    """
    def __init__(self):
        # self.current_grid_states = None
        self.current_sensor_states = None
        self.service_request_decision = None
        self.posted_service_list = []
        self.service_serial_num = 0
        self.manual_service_xml_data = {}
        self.already_posted_services = []
        self.deleted_items = []


    def update_sensor_states(self):
        """
        Retrieves measurement data from the Measurement Processor. The measurements are organized by topological group.
        """
        pass

    def make_service_request_decision(self):
        """
        In MANUAL MODE (override is True):
            Instantiates a grid service
        """
        if mcConfiguration.go_sensor_decision_making_manual_override is True:
            self.manually_post_service(edmTimekeeper.get_sim_current_time())
        elif mcConfiguration.go_sensor_decision_making_manual_override is False:
            pass
        else:
            print("Service request failure. Wrong input.")

        pass

    def load_manual_service_file(self):
        input_file = open(mcConfiguration.manual_service_filename, "r")
        data = input_file.read()
        input_file.close()
        self.manual_service_xml_data = xmltodict.parse(data)
        print(self.manual_service_xml_data)

    def manually_post_service(self, sim_time):
        for key, item in self.manual_service_xml_data['services'].items():
            print(item)
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
                self.posted_service_list.append(GOPostedService(name, group_id, service_type, interval_start, interval_duration, power, ramp, price))
                print("Manually posting service, name:")
                print(name)


class GOOutputInterface:
    """
    NOT YET IMPLEMENTED.
    API between the MC and a DERMS. Must be customized to the needs of the DERMS. Converts determinations and feedback
    data to message formats the DERMS requires/can use, and delivers them.
    """
    connection_status = None
    current_service_requests = []
    service_request_status = None


    def get_all_posted_service_requests(self):
        """

        """
        for item in goSensor.posted_service_list:
            if item.get_status() is False:
                print("Posting...")
                self.current_service_requests.append(item.get_service_message_data())
                print(item.get_service_message_data())
                item.set_status(True)
            else:
                print("All already posted")



    def generate_service_messages(self):
        """

        """
        request_out_xml = dict2xml(self.current_service_requests)
        print("Current Service Requests")
        print(request_out_xml)
        return request_out_xml

    def send_service_request_messages(self):
        """

        """
        xmlfile = open("toGSP.xml", "w")
        xmlfile.write(self.generate_service_messages())
        xmlfile.close()
        pass


class MCOutputLog:
    """
    Generates .csv logs containing measurements from the measurement processor. Updates (writes a line) once per
    timestep.
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
            if self.is_first_measurement is True:
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
            # print("skipping")
            pass

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
        self.append_timestamps()

    def translate_header_names(self):
        """
        Looks up the plain english names for the headers and provides them to a dictionary for use by write_header().
        TODO: Refactor?
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
        This is where you name the log.
        TODO: I don't really need a method for this, do I?
        """
        self.log_name = 'testlog.csv'

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
    TODO: Write this
    """
    def __init__(self, service_name="Undefined", group_id=0, service_type="Undefined", interval_start=0, interval_duration = 0, power=0, ramp=0, price=0):
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
    TODO: May take another crack at putting this in the edmCore object. It was a mess the first time I tried, due to
    challenges with getting the simulation ID before running the simulation.
    """
    global edmMeasurementProcessor
    edmMeasurementProcessor = EDMMeasurementProcessor(simulation_id, gapps_object)
    edmCore.gapps_session.subscribe(t.simulation_output_topic(edmCore.sim_mrid), edmMeasurementProcessor)
    global edmTimekeeper
    edmTimekeeper = EDMTimeKeeper(simulation_id, gapps_object, edmCore)
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
