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
    print("Second run...")
    try:
        ModelController.main(test_mode=False, DERSHDI_FilePath=r"DERSHistoricalData Inputs/TP_ME1_A_LogInput2.csv")
    except SystemExit:
        context.secondfilename = ModelController.mcConfiguration.output_log_name
        context.secondfilepath = context.MEPath + context.secondfilename
