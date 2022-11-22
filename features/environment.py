from behave import *
import ModelController

def before_all(context):
    context.MEPath = "/home/seanjkeene/PycharmProjects/doe-egot-me/"

    print("First run...")
    try:
        ModelController.main(test_mode=False, DERSHDI_FilePath=r"DERSHistoricalData Inputs/TP_ME1_A_LogInput.csv")
    except SystemExit:
        context.firstfilename = ModelController.mcConfiguration.output_log_name
        context.firstfilepath = context.MEPath + context.firstfilename
        context.firstTPME1UIR = ModelController.mcInputInterface.test_tpme1_unified_input_request

    try:
        ModelController.main(test_mode=False, DERSHDI_FilePath=r"DERSHistoricalData Inputs/TP_ME1_A_LogInput2.csv")
    except SystemExit:
        context.secondfilename = ModelController.mcConfiguration.output_log_name
        context.secondfilepath = context.MEPath + context.secondfilename
        context.secondTPME1UIR = ModelController.mcInputInterface.test_tpme1_unified_input_request


    # {'LOGDER0001': '0', 'LOGDER0001_loc': '632'}
    # {'00001': {'Filepath': 'DER00001_Bus633.csv', 'Bus': '633'},
    #  '00000': {'Filepath': 'DER00000_Bus632.csv', 'Bus': '632'}}
