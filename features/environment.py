from behave import *
import ModelController
import pandas
from melogtool import *
melogtool = MELogTool()
import os
import glob
import cProfile


def concatenate_logs(full_filepath):
    folder_path, filename = os.path.split(full_filepath)
    base_filename = os.path.splitext(filename)[0]

    # Find all files matching the pattern
    file_pattern = f"{base_filename}_[0-9]*.csv"
    files = glob.glob(f"{folder_path}/{file_pattern}")

    print("Folder Path:", folder_path)
    print("File Pattern:", file_pattern)
    print("Files:", files)

    # Sort the files in ascending order
    files.sort()
    # Create the new file
    new_filename = f"{folder_path}/{base_filename}.csv"
    with open(new_filename, 'w') as new_file:
        # Flag to indicate if header has been written
        header_written = False

        # Iterate over each file and append its contents to the new file
        for file in files:
            with open(file, 'r') as log_file:
                # Read the contents of the file
                file_contents = log_file.read()

                # Skip header row if already written
                if header_written:
                    file_contents = file_contents.split('\n', 1)[1]

                # Write the contents of the file to the new file
                new_file.write(file_contents)

                # # Print the contents of the file (optional)
                # print(file_contents)

                # Set header_written to True after writing the first file
                if not header_written:
                    header_written = True

    return new_filename


def before_all(context):
    environment_path = os.path.abspath(__file__)
    root_folder_path = os.path.dirname(os.path.dirname(environment_path))
    context.MEPath = root_folder_path + "/"
    print(context.MEPath)
    context.firstinputfilepath = r"DERSHistoricalData Inputs/ders_1000.csv"
    context.secondinputfilepath = r"DERSHistoricalData Inputs/ders_2000.csv"
    context.outputxmlpath = r"Outputs To DERMS/OutputtoGSP.xml"
    context.unique_ids = ['LOGDER0001_Watts', '00000', '00001']

    print("First run...")
    try:
        ModelController._main(test_mode=False, DERSHDI_FilePath=context.firstinputfilepath)
    except SystemExit:
        print("SYSTEMEXIT")
        context.firstfilename = ModelController.mcConfiguration.output_log_name
        context.firstfilepath = context.MEPath + context.firstfilename
        print(context.firstfilepath)
        context.firstTPME1UIR = ModelController.mcInputInterface.test_tpme1_unified_input_request
        print("context.firstTPME1UIR")
        print(context.firstTPME1UIR)
        print(ModelController.mcInputInterface.test_tpme1_unified_input_request)

    try:
        ModelController._main(test_mode=False, DERSHDI_FilePath=context.secondinputfilepath)
    except SystemExit:
        context.secondfilename = ModelController.mcConfiguration.output_log_name
        context.secondfilepath = context.MEPath + context.secondfilename
        context.secondTPME1UIR = ModelController.mcInputInterface.test_tpme1_unified_input_request

    context.first_parsed_output_df = melogtool.parse_logs(
        context.MEPath + "Log Tool Options Files/options.xml", concatenate_logs(context.firstfilepath))
    melogtool.parse_logs(context.MEPath + "Log Tool Options Files/options.xml", concatenate_logs(context.firstfilepath)).to_csv(
        'df_test.csv')
    melogtool.parse_logs(context.MEPath + "Log Tool Options Files/options.xml", concatenate_logs(context.firstfilepath)).to_csv(
        'df_test2.csv')
    context.parsed_logs_filename = 'df_test.csv'
    context.parsed_logs_filename2 = 'df_test2.csv'

    context.assignment_lookup_table = {}
    for item in ModelController.derAssignmentHandler.assignment_lookup_table:
        if 'house_name' in item:
            context.assignment_lookup_table[item['house_name']] = {'Bus': item['Bus'], 'mRID': item['house_mRID'],
                                                             'DER-EM Name': item['house_name']}
        elif 'DER_name' in item:
            context.assignment_lookup_table[item['DER_name']] = {'Bus': item['Bus'], 'mRID': item['DER_mRID'],
                                                             'DER-EM Name': item['DER_name']}
    context.association_lookup_table = ModelController.derIdentificationManager.association_lookup_table
    context.der_input_list = [
        'LOGDER0001_Watts',
        'LOGDER0001_VARs',
        '00000',
        '00001'
    ]
    context.der_em_list = [
        'DEREM_6344',
        'DEREM_6332',
        'test_3_phase_der'
        # 'DEREM_2p_6751',
        # 'DEREM_3p_6752'
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
