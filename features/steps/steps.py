from behave import *
from os import path
import ModelController
import melogtool

@given(u'DER-S inputs are available')
def step_impl(context):
    assert path.exists(
        "/home/seanjkeene/PycharmProjects/doe-egot-me/DERSHistoricalData Inputs/TP_ME1_A_LogInput.csv") is True
    assert path.exists(
        "/home/seanjkeene/PycharmProjects/doe-egot-me/DERSHistoricalData Inputs/TP_ME1_A_LogInput2.csv") is True
    assert path.exists(
        "/home/seanjkeene/PycharmProjects/doe-egot-me/RWHDERS Inputs/DER00000_Bus632.csv") is True
    assert path.exists(
        "/home/seanjkeene/PycharmProjects/doe-egot-me/RWHDERS Inputs/DER00001_Bus633.csv") is True


@when(u'A DER-S update occurs')
def step_impl(context):
    ModelController.mcInputInterface.update_all_der_s_status()


@then(u'The Unified Input Request should indicate an input request at the correct time')
def step_impl(context):
    pass  # The correct time is handled by the test interface added to ModelController.py


@then(u'The Unified Input Request should indicate an input request in the proper format')
def step_impl(context):
    assert type(context.firstTPME1UIR) is list
    for items in context.firstTPME1UIR:
        assert type(items) is dict
    for item in context.firstTPME1UIR:
        for i in item:
            assert type(i) is str
            assert type(item[i]) is str
            assert type(int(item[i])) is int


@then(u'The Unified Input Request should indicate an input request with the correct unique IDs and magnitudes.')
def step_impl(context):
    assert {'LOGDER0001': '10000000'} in context.firstTPME1UIR
    assert {'00000': '100000'} in context.firstTPME1UIR



@given(u'Output logs exist for two unique simulations')
def step_impl(context):
    assert path.exists(
        context.MEPath + context.firstfilename) is True
    assert path.exists(
        context.MEPath + context.secondfilename) is True


@given(u'DER Inputs for each simulation were not identical')
def step_impl(context):
    with open(context.firstfilepath, 'r') as file1, open(context.secondfilepath, 'r') as file2:
        file1contents = file1.readlines()
        file2contents = file2.readlines()
    x = 0
    for line in file2contents:
        if line != file1contents[x]:
            assert True is True
        x += 1
    assert False is True


@then(u'The logs should indicate proper values for each input.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The logs should indicate proper values for each input.')


@then(u'The Unified Input Request should indicate an input request with the correct unique IDs.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The Unified Input Request should indicate an input request with the correct '
                              u'unique IDs.')


@when(u'The DER-Ss configuration process occurs (as in simulation startup)')
def step_impl(context):
    pass # Performed in environment.py

@then(u'Each DER-S should contain information associating a Unique ID with a locational identifier')
def step_impl(context):
    assert ModelController.dersHistoricalDataInput.test_first_row['LOGDER0001_loc'] == '632'
    assert ModelController.rwhDERS.input_identification_dict['00000']['Bus'] == '632'


@given(u'The Model Controller has completed the simulation startup process.')
def step_impl(context):
    pass  # Done in environment.py


@then(u'A GridAPPS-D simulation object should be instantiated.')
def step_impl(context):/home/seanjkeene/PycharmProjects/doe-egot-melogtool
    print(ModelController.edmCore.gapps_session)
    print(type(ModelController.edmCore.gapps_session))
    assert ModelController.edmCore.gapps_session is not None


@then(u'Output logs should exist for two unique simulations')
def step_impl(context):
    assert path.exists(
        "/home/seanjkeene/PycharmProjects/doe-egot-me/" + context.firstfilename) is True
    assert path.exists(
        "/home/seanjkeene/PycharmProjects/doe-egot-me/" + context.secondfilename) is True


@given(u'Logs from a simulation using these DER Input files exist')
def step_impl(context):
    assert path.exists(
        context.MEPath + context.firstfilename) is True
    assert path.exists(
        context.MEPath + context.secondfilename) is True


@then(u'Log files should indicate values update regularly at defined intervals.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then Log files should indicate values update regularly at defined intervals.')


@given(u'Logs from a simulation exist')
def step_impl(context):
    assert path.exists(
        context.MEPath + context.secondfilename) is True


@then(u'Log files should indicate power and voltage readings exist for three phases of any bus.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then Log files should indicate power and voltage readings exist for three phases '
                              u'of any bus.')


@given(u'The "Config.txt" file is available')
def step_impl(context):
    assert ModelController.edmCore.config_parameters is not None


@when(u'The Model Controller runs a full simulation')
def step_impl(context):
    pass  # Done in environment.py


@then(u'The simulation should start at the proper start time')
def step_impl(context):
    assert ModelController.edmCore.sim_start_time == (
        ModelController.edmCore.config_parameters["simulation_config"]["start_time"]
    )


@then(u'The simulation should end at the proper end time (start time + duration)')
def step_impl(context):
    assert int(ModelController.edmCore.sim_current_time) == int(
        ModelController.edmCore.config_parameters["simulation_config"]["start_time"]) + int(
        ModelController.edmCore.config_parameters["simulation_config"]["duration"])


@then(u'The logs should contain non-zero values for Voltage for a non-DER asset')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The logs should contain non-zero values for Voltage for a non-DER asset')


@then(u'The logs should contain non-zero values for Power for a non-DER asset')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The logs should contain non-zero values for Power for a non-DER asset')


@given(u'DER Inputs exist which include a DER-EM that acts as a load, source, and storage')
def step_impl(context):
    assert path.exists(
        "/home/seanjkeene/PycharmProjects/doe-egot-me/DERSHistoricalData Inputs/TP_ME1_A_LogInput.csv") is True

@given(u'Logs from a simulation exist which use these inputs')
def step_impl(context):
    assert path.exists(
        context.MEPath + context.secondfilename) is True


@then(u'The logs should indicate the DER acted as a storage, load, and source.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The logs should indicate the DER acted as a storage, load, and source.')


@then(u'The logs should contain non-zero values for Voltage for a DER-EM')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The logs should contain non-zero values for Voltage for a DER-EM')


@then(u'The logs should contain non-zero values for Power for a DER-EM')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The logs should contain non-zero values for Power for a DER-EM')


@then(u'The voltage values on each phase for a single load should not be exactly equal')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then The voltage values on each phase for a single load should not be exactly equal')


@then(u'The power values on each phase for a single load should not be exactly equal')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then The power values on each phase for a single load should not be exactly equal')


@when(u'The DER assignment process is called')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The DER assignment process is called')


@then(u'The Assignment Lookup table should contain the name of each DER input')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The Assignment Lookup table should contain the name of each DER input')


@then(u'The Assignment Lookup Table should contain an mRID for each DER input')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The Assignment Lookup Table should contain an mRID for each DER input')


@then(u'The mRID of each input in the Assignment Lookup Table should not be identical to any other input in the table.')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then The mRID of each input in the Assignment Lookup Table should not be identical to any other input '
        u'in the table.')


@then(u'Each DER-EM name should be associated with a locational identifier in the Assignment Lookup Table.')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then Each DER-EM name should be associated with a locational identifier in the Assignment Lookup Table.')


@given(u'Grid services need to be dispatched')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given Grid services need to be dispatched')


@when(u'The GO dispatches a grid service request')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The GO dispatches a grid service request')


@then(u'The GO should output an XML file available for use by the GSP.')
def step_impl(context):
    assert path.exists(
        context.MEPath + "Outputs To Derms/OutputtoGSP.xml") is True


@given(u'A manually posted service input file is available')
def step_impl(context):
    assert path.exists(
        context.MEPath + "manually_posted_service_input.xml") is True


@when(u'The function to manually post a service is called')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The function to manually post a service is called')


@then(u'A GOPostedService object should be instantiated')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then A GOPostedService object should be instantiated')


@when(u'The EDMTimeKeeper on-timestep function is called')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The EDMTimeKeeper on-timestep function is called')


@when(u'The EDMMeasurementProcessor measurement processing function is called')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The EDMMeasurementProcessor measurement processing function is called')


@then(u'On-timestep updates should occur')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then On-timestep updates should occur')


@then(u'New processed measurements should be available')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then New processed measurements should be available')


@then(u'A new unified input request should be generated')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then A new unified input request should be generated')


@then(u'The GOSensor should attempt to create a new GOPostedService object if applicable')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then The GOSensor should attempt to create a new GOPostedService object if applicable')


@then(u'GOOutputInterface should generate an output message')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then GOOutputInterface should generate an output message')


@given(u'The EDMMeasurementProcessor has received at least one set of measurements.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given The EDMMeasurementProcessor has received at least one set of measurements.')


@then(u'The EDMMeasurementProcessor should provide measurements by a function call')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The EDMMeasurementProcessor should provide measurements by a function call')


@then(u'The measurements should have human-readable names (not mRIDs).')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The measurements should have human-readable names (not mRIDs).')


@when(u'The DER-S input processing method is called')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The DER-S input processing method is called')


@when(u'The GOSensor grid service request method is called')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The GOSensor grid service request method is called')


@then(u'The unified input request should update')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The unified input request should update')


@then(u'The logs should indicate a DER-S changed state from one timestep to the next.')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then The logs should indicate a DER-S changed state from one timestep to the next.')


@then(u'The logs should indicate the DER-S updated at the right time in the input file.')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then The logs should indicate the DER-S updated at the right time in the input file.')


@given(u'A ME simulation is running.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given A ME simulation is running.')


@when(u'A measurement timestep--three seconds-- elapses.')
def step_impl(context):
    raise NotImplementedError(u'STEP: When A measurement timestep--three seconds-- elapses.')


@then(
    u'Measurements are placed in a dictionary in the EDMMeasurementProcessor class, which are then printed to the '
    u'terminal by a test function.')
def step_impl(context):
    raise NotImplementedError(
        u'STEP: Then Measurements are placed in a dictionary in the EDMMeasurementProcessor class, which are then '
        u'printed to the terminal by a test function.')


@when(u'The EDMTimeKeeper\'s on-timestep function is called')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The EDMTimeKeeper\'s on-timestep function is called')


@then(u'Time is incremented by one second')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then Time is incremented by one second')


@when(u'A DER-S calls the assignment function')
def step_impl(context):
    pass  # Performed in environment.py


@then(u'The DER association table contains keys for each input DER name')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The DER association table contains keys for each input DER name')


@then(u'The DER association table contains mRIDs associated with each name')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The DER association table contains mRIDs associated with each name')
