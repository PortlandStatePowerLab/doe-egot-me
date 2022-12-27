from behave import *
import ModelController
import pandas
from melogtool import *
melogtool = MELogTool()


def before_all(context):
    context.MEPath = "/home/seanjkeene/PycharmProjects/doe-egot-me/"
    context.firstinputfilepath = r"DERSHistoricalData Inputs/TP_ME1_A_LogInput.csv"
    context.secondinputfilepath = r"DERSHistoricalData Inputs/TP_ME1_A_LogInput2.csv"
    context.unique_ids = ['LOGDER0001', '00000', '00001']

    print("First run...")
    try:
        ModelController.main(test_mode=False, DERSHDI_FilePath=context.firstinputfilepath)
    except SystemExit:
        context.firstfilename = ModelController.mcConfiguration.output_log_name
        context.firstfilepath = context.MEPath + context.firstfilename
        context.firstTPME1UIR = ModelController.mcInputInterface.test_tpme1_unified_input_request

    try:
        ModelController.main(test_mode=False, DERSHDI_FilePath=context.secondinputfilepath)
    except SystemExit:
        context.secondfilename = ModelController.mcConfiguration.output_log_name
        context.secondfilepath = context.MEPath + context.secondfilename
        context.secondTPME1UIR = ModelController.mcInputInterface.test_tpme1_unified_input_request

    context.first_parsed_output_df = melogtool.parse_logs(
        context.MEPath + "Log Tool Options Files/options.xml", context.firstfilepath)
    melogtool.parse_logs(context.MEPath + "Log Tool Options Files/options.xml", context.firstfilepath).to_csv(
        'df_test.csv')
    context.assignment_lookup_table = {}
    for item in ModelController.derAssignmentHandler.assignment_lookup_table:
        context.assignment_lookup_table[item['Name']] = {'Bus': item['Bus'], 'mRID': item['mRID'], 'DER-EM Name': item['DER-EM Name']}
    context.association_lookup_table = ModelController.derIdentificationManager.association_lookup_table
    context.der_input_list = [
        'LOGDER0001',
        '00000',
        '00001'
    ]
    context.der_em_list = [
        'DER_RWHDERS_Test_6332_Battery',
        'DER_Association_Test_6322_Battery',
        'DER_Association_Test_6331_Battery'
    ]

    context.posted_service_list = ModelController.goSensor.posted_service_list
