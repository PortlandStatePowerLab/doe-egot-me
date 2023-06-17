from behave import *
import ModelController
import pandas
from melogtool import *
melogtool = MELogTool()


def before_all(context):
    context.MEPath = "/root/PycharmProjects/doe-egot-me/"
    context.firstinputfilepath = r"DERSHistoricalData Inputs/TP_ME1_A_LogInput.csv"
    context.secondinputfilepath = r"DERSHistoricalData Inputs/TP_ME1_A_LogInput2.csv"
    context.outputxmlpath = r"Outputs To DERMS/OutputtoGSP.xml"
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
    melogtool.parse_logs(context.MEPath + "Log Tool Options Files/options.xml", context.firstfilepath).to_csv(
        'df_test2.csv')
    context.parsed_logs_filename = 'df_test.csv'
    context.parsed_logs_filename2 = 'df_test2.csv'

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
        'DEREM_6321_Battery',
        'DEREM_6331_Battery',
        'DEREM_6341_Battery',
        'DEREM_2p_6751_Battery',
        'DEREM_3p_6752_Battery'
    ]

    context.posted_service_list = ModelController.goSensor.posted_service_list

    context.list_of_models = ModelController.edmCore.gapps_session.query_data(
        '''
        PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX c:  <http://iec.ch/TC57/CIM100#>
        SELECT ?feeder ?fid ?station ?sid ?subregion ?sgrid ?region ?rgnid WHERE {
         ?s r:type c:Feeder.
         ?s c:IdentifiedObject.name ?feeder.
         ?s c:IdentifiedObject.mRID ?fid.
         ?s c:Feeder.NormalEnergizingSubstation ?sub.
         ?sub c:IdentifiedObject.name ?station.
         ?sub c:IdentifiedObject.mRID ?sid.
         ?sub c:Substation.Region ?sgr.
         ?sgr c:IdentifiedObject.name ?subregion.
         ?sgr c:IdentifiedObject.mRID ?sgrid.
         ?sgr c:SubGeographicalRegion.Region ?rgn.
         ?rgn c:IdentifiedObject.name ?region.
         ?rgn c:IdentifiedObject.mRID ?rgnid.
}
ORDER by ?station ?feeder
        '''
    )
