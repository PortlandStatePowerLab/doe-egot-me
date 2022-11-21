from behave import *
from os import path
import ModelController


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
    raise NotImplementedError(u'STEP: Then The Unified Input Request should indicate an input request at the correct time')


@then(u'The Unified Input Request should indicate an input request in the proper format')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The Unified Input Request should indicate an input request in the proper format')


@then(u'The Unified Input Request should indicate an input request with the correct unique IDs and magnitudes.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The Unified Input Request should indicate an input request with the correct unique IDs and magnitudes.')


@given(u'Output logs exist for two unique simulations')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given Output logs exist for two unique simulations')


@given(u'DER Inputs for each simulation were not identical')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given DER Inputs for each simulation were not identical')


@then(u'The logs should indicate proper values for each input.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The logs should indicate proper values for each input.')


@then(u'The Unified Input Request should indicate an input request with the correct unique IDs.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The Unified Input Request should indicate an input request with the correct unique IDs.')


@when(u'The DER-Ss configuration process occurs (as in simulation startup)')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The DER-Ss configuration process occurs (as in simulation startup)')


@then(u'Each DER-S should contain information associating a Unique ID with a locational identifier')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then Each DER-S should contain information associating a Unique ID with a locational identifier')


@given(u'The Model Controller has completed the simulation startup process.')
def step_impl(context):
    pass  # See environment.py


@then(u'A GridAPPS-D simulation object should be instantiated.')
def step_impl(context):
    print(ModelController.edmCore.gapps_session)
    print(type(ModelController.edmCore.gapps_session))
    assert ModelController.edmCore.gapps_session is not None


@then(u'Output logs should exist for two unique simulations')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then Output logs should exist for two unique simulations')


@given(u'DER Input files exist')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given DER Input files exist')


@given(u'Logs from a simulation using these DER Input files exist')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given Logs from a simulation using these DER Input files exist')


@then(u'Log files should indicate values update regularly at defined intervals.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then Log files should indicate values update regularly at defined intervals.')


@given(u'Logs from a simulation exist')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given Logs from a simulation exist')


@then(u'Log files should indicate power and voltage readings exist for three phases of any bus.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then Log files should indicate power and voltage readings exist for three phases of any bus.')


@given(u'The "Config.txt" file is available')
def step_impl(context):
    assert ModelController.edmCore.config_parameters is not None


@when(u'The Model Controller runs a full simulation')
def step_impl(context):
    pass  # See environment.py


@then(u'The simulation should start at the proper start time')
def step_impl(context):

    assert ModelController.edmCore.sim_start_time == ModelController.edmCore.config_parameters["simulation_config"]["start_time"]


@then(u'The simulation should end at the proper end time (start time + duration)')
def step_impl(context):
    assert int(ModelController.edmCore.sim_current_time) == int(ModelController.edmCore.config_parameters["simulation_config"]["start_time"]) + int(ModelController.edmCore.config_parameters["simulation_config"]["duration"])


@then(u'The logs should contain non-zero values for Voltage for a non-DER asset')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The logs should contain non-zero values for Voltage for a non-DER asset')


@then(u'The logs should contain non-zero values for Power for a non-DER asset')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The logs should contain non-zero values for Power for a non-DER asset')


@given(u'DER Inputs exist which include a DER-EM that acts as a load, source, and storage')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given DER Inputs exist which include a DER-EM that acts as a load, source, and storage')


@given(u'Logs from a simulation exist which use these inputs')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given Logs from a simulation exist which use these inputs')


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
    raise NotImplementedError(u'STEP: Then The voltage values on each phase for a single load should not be exactly equal')


@then(u'The power values on each phase for a single load should not be exactly equal')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The power values on each phase for a single load should not be exactly equal')


@given(u'DER Inputs are available')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given DER Inputs are available')


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
    raise NotImplementedError(u'STEP: Then The mRID of each input in the Assignment Lookup Table should not be identical to any other input in the table.')



@then(u'Each DER-EM name should be associated with a locational identifier in the Assignment Lookup Table.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then Each DER-EM name should be associated with a locational identifier in the Assignment Lookup Table.')


@given(u'Grid services need to be dispatched')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given Grid services need to be dispatched')


@when(u'The GO dispatches a grid service request')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The GO dispatches a grid service request')


@then(u'The GO should output an XML file available for use by the GSP.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The GO should output an XML file available for use by the GSP.')


@given(u'A manually posted service input file is available')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given A manually posted service input file is available')


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
    raise NotImplementedError(u'STEP: Then The GOSensor should attempt to create a new GOPostedService object if applicable')


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


@given(u'A DER Input is available')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given A DER Input is available')


@given(u'A grid service input file is available')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given A grid service input file is available')


@when(u'The DER-S input processing method is called')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The DER-S input processing method is called')


@when(u'The GOSensor grid service request method is called')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The GOSensor grid service request method is called')


@then(u'The unified input request should update')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The unified input request should update')


@then(u'A GO output XML file should be generated')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then A GO output XML file should be generated')


@then(u'The logs should indicate a DER-S changed state from one timestep to the next.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The logs should indicate a DER-S changed state from one timestep to the next.')


@then(u'The logs should indicate the DER-S updated at the right time in the input file.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The logs should indicate the DER-S updated at the right time in the input file.')


@given(u'A ME simulation is running.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given A ME simulation is running.')


@when(u'A measurement timestep--three seconds-- elapses.')
def step_impl(context):
    raise NotImplementedError(u'STEP: When A measurement timestep--three seconds-- elapses.')


@then(u'Measurements are placed in a dictionary in the EDMMeasurementProcessor class, which are then printed to the terminal by a test function.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then Measurements are placed in a dictionary in the EDMMeasurementProcessor class, which are then printed to the terminal by a test function.')


@when(u'The EDMTimeKeeper\'s on-timestep function is called')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The EDMTimeKeeper\'s on-timestep function is called')


@then(u'Time is incremented by one second')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then Time is incremented by one second')


@given(u'DER Input files are available')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given DER Input files are available')


@when(u'A DER-S calls the assignment function')
def step_impl(context):
    raise NotImplementedError(u'STEP: When A DER-S calls the assignment function')


@then(u'The DER association table contains keys for each input DER name')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The DER association table contains keys for each input DER name')


@then(u'The DER association table contains mRIDs associated with each name')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The DER association table contains mRIDs associated with each name')
