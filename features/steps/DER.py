from behave import *
import ModelController

@given(u'A simulation is running which includes at least one DER-S')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given A simulation is running which includes at least one DER-S')


@when(u'The DER-S receives updated DER states from an external source (such as an emulator, file, or physical system).')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The DER-S receives updated DER states from an external source (such as an emulator, file, or physical system).')


@then(u'The associated DER-EMs update to reflect the updated DER states as seen by the MC logs.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The associated DER-EMs update to reflect the updated DER states as seen by the MC logs.')


@given(u'A test is running which includes at least one DER-S.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given A test is running which includes at least one DER-S.')


@when(u'A DER-S retrieves data from an external system, program or file.')
def step_impl(context):
    raise NotImplementedError(u'STEP: When A DER-S retrieves data from an external system, program or file.')


@then(u'The DER-S produces an updated electrical representation of the DER as viewed by the terminal or in logs.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The DER-S produces an updated electrical representation of the DER as viewed by the terminal or in logs.')


@then(u'Unique identifiers are provided to the assignment handler class representing each DER within each DER-S.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then Unique identifiers are provided to the assignment handler class representing each DER within each DER-S.')


@then(u'Correct locational identifiers are provided to the assignment handler class representing each DER within each DER-S.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then Correct locational identifiers are provided to the assignment handler class representing each DER within each DER-S.')


@given(u'An API has been developed between the DER-S and a physical controller for a DER. A ME simulation is underway.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given An API has been developed between the DER-S and a physical controller for a DER. A ME simulation is underway.')


@when(u'The physical controller sends data to the DER-S.')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The physical controller sends data to the DER-S.')


@then(u'The DER-S produces an updated electrical representation of the physical DER as viewed by the terminal or in logs.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The DER-S produces an updated electrical representation of the physical DER as viewed by the terminal or in logs.')


@given(u'An API has been developed between the DER-S and a DER emulator script. A ME simulation is underway.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given An API has been developed between the DER-S and a DER emulator script. A ME simulation is underway.')


@when(u'The script sends data to the DER-S.')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The script sends data to the DER-S.')


@then(u'The DER-S produces an updated electrical representation of the simulated or emulated DER as viewed by the terminal or in logs.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The DER-S produces an updated electrical representation of the simulated or emulated DER as viewed by the terminal or in logs.')


@given(u'An API has been developed between the DER-S and a file containing DER historical data. A ME simulation is underway.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given An API has been developed between the DER-S and a file containing DER historical data. A ME simulation is underway.')


@when(u'The DER-S reads the historical data file.')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The DER-S reads the historical data file.')


@then(u'The DER-S produces an updated electrical representation of the data-represented DER as viewed by the terminal or in logs.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The DER-S produces an updated electrical representation of the data-represented DER as viewed by the terminal or in logs.')


@given(u'An API has been developed between the DER-S and a DERMS. A ME simulation is underway.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given An API has been developed between the DER-S and a DERMS. A ME simulation is underway.')


@when(u'The DERMS sends data to the DER-S.')
def step_impl(context):
    raise NotImplementedError(u'STEP: When The DERMS sends data to the DER-S.')


@then(u'The DER-S produces an updated electrical representation of the DERMS message as viewed by the terminal or in logs.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then The DER-S produces an updated electrical representation of the DERMS message as viewed by the terminal or in logs.')
