from behave import *
import ModelController

@given('an RWHDERS input exists')
def step_impl(context):
    try:
        ModelController.main(test_mode=True)
    except(SystemExit):
        pass
    context.rwhders_input = ModelController.rwhDERS.input_identification_dict[list(ModelController.rwhDERS.input_identification_dict.keys())[0]]['Filepath']
    assert type(context.rwhders_input) is str


@when(u'RWHDERS processes an input')
def step_impl(context):
    context.rwhders_output = ModelController.rwhDERS.get_input_request()


@then(u'RWHDERS should output a message in the right format')
def step_impl(context):
    for item in context.rwhders_output:
        for key, value in item.items():
            assert type(key) is str
            assert type(value) is str
            assert type(int(value)) is int


@given(u'a DERHistoricalDataInput input exists')
def step_impl(context):
    assert ModelController.dersHistoricalDataInput.historical_data_file_path is not None

@when(u'DERHistoricalDataInput processes an input')
def step_impl(context):
    ModelController.dersHistoricalDataInput.update_der_em_input_request(force_first_row=True)
    context.dershist_output = ModelController.dersHistoricalDataInput.der_em_input_request
    print(context.dershist_output)

@then(u'DERHistoricalDataInput should output a message in the right format')
def step_impl(context):
    for item in context.dershist_output:
        for key, value in item.items():
            print(key)
            print(value)
            assert type(key) is str
            assert type(value) is str
            assert type(int(value)) is int