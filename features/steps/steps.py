from behave import *
from os import path
import ModelController
from melogtool import *
melogtool = MELogTool()
import csv
from datetime import datetime, timedelta

@given(u'DER-S inputs are available')
def step_impl(context):
    assert path.exists(
        context.MEPath + "DERSHistoricalData Inputs/ders_1000.csv") is True
    assert path.exists(
        context.MEPath + "DERSHistoricalData Inputs/ders_2000.csv") is True
    assert path.exists(
        context.MEPath + "RWHDERS Inputs/DER00000_Bus632.csv") is True
    assert path.exists(
        context.MEPath + "RWHDERS Inputs/DER00001_Bus633.csv") is True


@when(u'A DER-S update occurs')
def step_impl(context):
    ModelController.mcInputInterface.update_all_der_s_status()


@then(u'The Unified Input Request should indicate an input request at the correct time')
def step_impl(context):
    pass  # The correct time is handled by the test interface added to ModelController.py


@then(u'The Unified Input Request should indicate an input request in the proper format')
def step_impl(context):
    print(context.firstTPME1UIR)
    assert type(context.firstTPME1UIR) is dict
    for items in context.firstTPME1UIR:
        print(items)
        assert type(items) is str
    for key, value in context.firstTPME1UIR.items():
        assert type(key) is str
        assert type(int(value)) is int


@then(u'The Unified Input Request should indicate an input request with the correct unique IDs and magnitudes.')
def step_impl(context):
    print("FIRST TPME1UIR")
    print(context.firstTPME1UIR)

    assert int(context.firstTPME1UIR['LOGDER0001_Watts']) == 1000
    assert int(context.firstTPME1UIR['00000']) == 100000



@given(u'Output logs exist for two unique simulations')
def step_impl(context):
    print(context.MEPath)
    print(context.firstfilename)
    assert path.exists(
        context.MEPath + context.firstfilename + "_1.csv") is True
    assert path.exists(
        context.MEPath + context.secondfilename + "_1.csv") is True


@given(u'DER Inputs for each simulation were not identical')
def step_impl(context):
    with open(context.firstinputfilepath, 'r') as file1, open(context.secondinputfilepath, 'r') as file2:
        file1contents = file1.readlines()
        file2contents = file2.readlines()
    x = 0
    same_count = 0
    for line in file2contents:
        if line != file1contents[x]:
            assert True is True
        else:
            same_count += 1
        x += 1
    if (same_count == len(file2contents)) or (same_count == len(file1contents)):
        print(same_count)
        print(len(file1contents))
        assert False is True


@then(u'The logs should indicate proper values for each input.')
def step_impl(context):
    def parse_input_file(input_file):
        changes = []
        with open(input_file, 'r') as file:
            reader = csv.DictReader(file)
            header = reader.fieldnames
            magnitude_col = None
            for col in header:
                if col not in ['Time', 'Location'] and not col.endswith('_loc'):
                    magnitude_col = col
                    break

            if magnitude_col is None:
                raise Exception("Magnitude column not found.")

            prev_magnitude = None
            for row in reader:
                time_str = row['Time']
                magnitude = float(row[magnitude_col])
                time = datetime.utcfromtimestamp(int(time_str))
                if prev_magnitude is not None and magnitude != prev_magnitude:
                    changes.append({'Time': time, 'Magnitude': magnitude})
                prev_magnitude = magnitude
        return changes

    def parse_output_file(output_file, input_changes):
        with open(output_file, 'r') as file:
            reader = csv.DictReader(file)
            header = reader.fieldnames
            magnitude_cols = [col for col in header if col.endswith('[magnitude]')]

            for input_change in input_changes:
                input_time = input_change['Time']
                input_magnitude = input_change['Magnitude']

                matched_magnitude_found = False
                closest_magnitude = None
                closest_col = None
                closest_timestamp = None
                min_magnitude_diff = float('inf')

                for row in reader:
                    timestamp_str = row['Timestamp']
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

                    if input_time <= timestamp <= input_time + timedelta(seconds=5):
                        for col in magnitude_cols:
                            magnitude = float(row[col])
                            magnitude_diff = abs(magnitude - input_magnitude / 3)
                            relative_threshold = 0.01 * abs(input_magnitude / 3)
                            if magnitude_diff <= relative_threshold:
                                matched_magnitude_found = True
                                min_magnitude_diff = magnitude_diff
                                closest_magnitude = magnitude
                                closest_col = col
                                closest_timestamp = timestamp
                                break  # Exit the inner loop if a match is found

                        if not matched_magnitude_found and magnitude_diff <= min_magnitude_diff:
                            min_magnitude_diff = magnitude_diff
                            closest_magnitude = magnitude
                            closest_col = col
                            closest_timestamp = timestamp

                if matched_magnitude_found:
                    print(f"Match found for input timestamp {input_time}. Input Magnitude: {input_magnitude}")
                else:
                    if closest_magnitude is not None:
                        raise Exception(
                            f"No matching magnitude found within time delta for input timestamp {input_time}. Input Magnitude: {input_magnitude}\nClosest magnitude found: {closest_magnitude} in column {closest_col}, timestamp: {closest_timestamp}\nClosest magnitude difference: {min_magnitude_diff}")
                    else:
                        raise Exception(
                            f"No matching magnitude found within time delta for input timestamp {input_time}. Input Magnitude: {input_magnitude}\nNo closest magnitude found within the time delta.")

                file.seek(0)
                next(reader)  # Skip the header row

    # Input file paths
    input_1a_file = "DERSHistoricalData Inputs/ders_1000.csv"
    input_2a_file = "DERSHistoricalData Inputs/ders_2000.csv"
    output_1b_file = "df_test.csv"
    output_2b_file = "df_test2.csv"

    # Parse input files
    changes_1a = parse_input_file(input_1a_file)
    changes_2a = parse_input_file(input_2a_file)

    # Parse output files
    parse_output_file(output_1b_file, changes_1a)
    parse_output_file(output_2b_file, changes_2a)


@then(u'The Unified Input Request should indicate an input request with the correct unique IDs.')
def step_impl(context):

    # for i in context.firstTPME1UIR:
    print(context.firstTPME1UIR)
    print(context.firstTPME1UIR.keys())
    # print(i)
    # unique_id = list(i.keys())
    unique_id = list(context.firstTPME1UIR.keys())
    for i in range(len(unique_id)):
        print(range(len(unique_id)))
        print(unique_id[i])
        print(context.unique_ids)
        if unique_id[i] in context.unique_ids:
            print("Removing:")
            print(i)
            print(context.unique_ids)
            context.unique_ids.remove(unique_id[i])
            print(context.unique_ids)
        else:
            print("Excess unique ID found. Ensure system is in test configuration.")
            assert True is False
    print(len(context.unique_ids))
    assert len(context.unique_ids) == 0


@when(u'The DER-Ss configuration process occurs (as in simulation startup)')
def step_impl(context):
    pass # Performed in environment.py

@then(u'Each DER-S should contain information associating a Unique ID with a locational identifier')
def step_impl(context):
    print(ModelController.dersHistoricalDataInput.test_first_row)
    assert ModelController.dersHistoricalDataInput.test_first_row['LOGDER0001_loc'] == 'n634'
    assert ModelController.rwhDERS.input_identification_dict['00000']['Bus'] == 'n632'


@given(u'The Model Controller has completed the simulation startup process.')
def step_impl(context):
    pass  # Done in environment.py


@then(u'A GridAPPS-D simulation object should be instantiated.')
def step_impl(context):
    print(ModelController.edmCore.gapps_session)
    print(type(ModelController.edmCore.gapps_session))
    assert ModelController.edmCore.gapps_session is not None


@then(u'Output logs should exist for two unique simulations')
def step_impl(context):
    assert path.exists(
        "/root/PycharmProjects/doe-egot-me/" + context.firstfilename) is True
    assert path.exists(
        "/root/PycharmProjects/doe-egot-me/" + context.secondfilename) is True


@given(u'Logs from a simulation using these DER Input files exist')
def step_impl(context):
    assert path.exists(
        context.MEPath + context.firstfilename + "_1.csv") is True
    assert path.exists(
        context.MEPath + context.secondfilename + "_1.csv") is True


@then(u'Log files should indicate values update regularly at defined intervals.')
def step_impl(context):
    # Open the CSV file
    filename = context.parsed_logs_filename  # Replace with your file name
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        # Get the fieldnames excluding the first column (assumed to be the index column)
        fieldnames = [column for column in reader.fieldnames[1:] if column.lower().endswith(('[magnitude]', '[angle]'))]

        # Initialize variables
        prev_measurements = {}
        prev_timestamp = None
        three_second_interval = timedelta(seconds=3)
        changes = []

        # Iterate over rows
        for row in reader:
            timestamp_str = row['Timestamp']

            # Skip the header row
            if timestamp_str == 'Timestamp':
                continue

            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

            # Skip the first row
            if prev_measurements == {}:
                prev_measurements = {column: row[column] for column in fieldnames}
                prev_timestamp = timestamp
                continue

            # Check if three seconds have passed
            if timestamp - prev_timestamp >= three_second_interval:
                # Check for changes in magnitude
                magnitude_changed = False
                for column in fieldnames:
                    if '[magnitude]' in column and row[column] != prev_measurements[column]:
                        changes.append({
                            'Time': prev_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            'Column': column,
                            'Previous Value': prev_measurements[column],
                            'Current Value': row[column]
                        })
                        magnitude_changed = True
                        break

                # Check for changes in angle if no magnitude changes occurred
                if not magnitude_changed:
                    for column in fieldnames:
                        if '[angle]' in column and row[column] != prev_measurements[column]:
                            changes.append({
                                'Time': prev_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                                'Column': column,
                                'Previous Value': prev_measurements[column],
                                'Current Value': row[column]
                            })
                            break

                # If no difference found, raise an exception
                if not magnitude_changed and '[angle]' not in column:
                    raise Exception(f"No difference found for the three-second interval ending at {prev_timestamp}.")

                # Update previous measurements and timestamp
                prev_measurements = {column: row[column] for column in fieldnames}
                prev_timestamp = timestamp

        # Print the changes
        for change in changes:
            print(change)


@given(u'Logs from a simulation exist')
def step_impl(context):
    assert path.exists(
        context.MEPath + context.secondfilename + "_1.csv") is True


@then(u'Log files should indicate power and voltage readings exist for three phases of any bus.')
# Make Portable
def step_impl(context):
    print(context.first_parsed_output_df)
    headings_list = context.first_parsed_output_df.columns
    print(headings_list)
    heading_verification_list = [
         'PowerElectronicsConnection_BatteryUnit_DEREM_6332_A_VA[angle]',
         'PowerElectronicsConnection_BatteryUnit_DEREM_6332_A_VA[magnitude]',
         'PowerElectronicsConnection_BatteryUnit_DEREM_6332_C_VA[angle]',
         'PowerElectronicsConnection_BatteryUnit_DEREM_6332_C_VA[magnitude]',
         'PowerElectronicsConnection_BatteryUnit_DEREM_6332_C_PNV[angle]',
         'PowerElectronicsConnection_BatteryUnit_DEREM_6332_C_PNV[magnitude]',
         'PowerElectronicsConnection_BatteryUnit_DEREM_6332_B_VA[angle]',
         'PowerElectronicsConnection_BatteryUnit_DEREM_6332_B_VA[magnitude]',
         'PowerElectronicsConnection_BatteryUnit_DEREM_6332_A_PNV[angle]',
         'PowerElectronicsConnection_BatteryUnit_DEREM_6332_A_PNV[magnitude]',
         'PowerElectronicsConnection_BatteryUnit_DEREM_6332_B_PNV[angle]',
         'PowerElectronicsConnection_BatteryUnit_DEREM_6332_B_PNV[magnitude]'
                                ]
    for item in heading_verification_list:
        print(item)
        assert item in headings_list




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
    column = context.first_parsed_output_df.loc[:, "EnergyConsumer_house_680_b_20_s1_VA[magnitude]"]
    assert column.nunique() > 1


@then(u'The logs should contain non-zero values for Power for a non-DER asset')
def step_impl(context):
    column = context.first_parsed_output_df.loc[:, "EnergyConsumer_house_680_b_20_s1_PNV[magnitude]"]
    assert column.nunique() > 1

@given(u'DER Inputs exist which include a DER-EM that acts as a load, source, and storage')
def step_impl(context):
    assert path.exists(
        context.MEPath + "DERSHistoricalData Inputs/ders_1000.csv") is True

@given(u'Logs from a simulation exist which use these inputs')
def step_impl(context):
    assert path.exists(
        context.MEPath + context.secondfilename + "_1.csv") is True


@then(u'The logs should indicate the DER acted as a load and source.')
def step_impl(context):
    import csv

    # Constants
    input_file = context.parsed_logs_filename
    # Read the CSV file
    with open(input_file, 'r') as file:
        reader = csv.DictReader(file)
        header = reader.fieldnames

        # Find columns with magnitudes
        magnitude_cols = [col for col in header if col.endswith('[magnitude]')]

        # Variables to track positive and negative values
        positive_value_found = False
        negative_value_found = False
        positive_value = None
        negative_value = None
        column_name = None

        # Iterate over magnitude columns
        for col in magnitude_cols:
            positive_value_found = False
            negative_value_found = False

            # Iterate over rows in the current column
            for row in reader:
                magnitude = float(row[col])

                # Check for positive and negative values
                if magnitude > 0:
                    positive_value_found = True
                    positive_value = magnitude
                elif magnitude < 0:
                    negative_value_found = True
                    negative_value = magnitude

                # If both positive and negative values found, break the loop
                if positive_value_found and negative_value_found:
                    column_name = col
                    break

            # Reset the reader to the beginning of the file
            file.seek(0)
            next(reader)  # Skip the header row

            # If both positive and negative values found, break the outer loop
            if positive_value_found and negative_value_found:
                break

        # Check if both positive and negative values were found in a column
        if positive_value_found and negative_value_found:
            print(f"Column: {column_name}")
            print(f"First Positive Value: {positive_value}")
            print(f"First Negative Value: {negative_value}")
        else:
            raise Exception("No column with at least one positive and one negative value found.")


@then(u'The logs should contain non-zero values for Voltage for a DER-EM')
# Make Portable
def step_impl(context):
    # Define the row index
    row_index = 1

    # Define the header pattern for the new header
    header_pattern = r'^PowerElectronicsConnection_BatteryUnit_DEREM_6332_A_PNV\[magnitude\]$'

    # Use regular expression to find matching columns
    matching_columns = context.first_parsed_output_df.filter(regex=header_pattern, axis=1)

    # Check if the matching column exists in the DataFrame
    if matching_columns.empty:
        print("Matching column not found.")
        assert True == False
    else:
        # Get the value at the specified row_index and matching column
        value = matching_columns.iloc[row_index, 0]
        print("Value:", value)

        # Assert that the value is not equal to 0
        assert value != 0



@then(u'The logs should contain non-zero values for Power for a DER-EM')
# Make Portable
def step_impl(context):
    # Define the row index
    row_index = 1

    # Define the header pattern
    header_pattern = r'^PowerElectronicsConnection_BatteryUnit_DEREM_6332_A_VA\[magnitude\]$'

    # Use regular expression to find matching columns
    matching_columns = context.first_parsed_output_df.filter(regex=header_pattern, axis=1)

    # Check if the matching column exists in the DataFrame
    if matching_columns.empty:
        print("Matching column not found.")
        assert True == False
    else:
        # Get the value at the specified row_index and matching column
        value = matching_columns.iloc[row_index, 0]
        print("Value:", value)

        # Assert that the value is not equal to 0 (this will fail now)
        assert value != 0


@then(u'The voltage values on each phase for a single load should not be exactly equal')
def step_impl(context):
    print(context.first_parsed_output_df)
    row_index = 1
    header_pattern_v1 = r'^PowerElectronicsConnection_BatteryUnit_DEREM_3p_6752.*_A_PNV\[magnitude\]$'
    header_pattern_v2 = r'^PowerElectronicsConnection_BatteryUnit_DEREM_3p_6752.*_B_PNV\[magnitude\]$'
    header_pattern_v3 = r'^PowerElectronicsConnection_BatteryUnit_DEREM_3p_6752.*_C_PNV\[magnitude\]$'
    v1 = context.first_parsed_output_df.filter(regex=header_pattern_v1, axis=1).iloc[row_index, 0]
    v2 = context.first_parsed_output_df.filter(regex=header_pattern_v2, axis=1).iloc[row_index, 0]
    v3 = context.first_parsed_output_df.filter(regex=header_pattern_v3, axis=1).iloc[row_index, 0]
    print(v1)
    print(v2)
    print(v3)
    assert v1 != v2
    assert v2 != v3
    assert v1 != v3

@then(u'The power values on each phase for a single load should not be exactly equal')
def step_impl(context):
    # Define the row index
    row_index = 1

    # Define the header patterns
    header_pattern_p1 = r'^PowerElectronicsConnection_BatteryUnit_DEREM_3p_6752.*_C_VA\[magnitude\]$'
    header_pattern_p2 = r'^PowerElectronicsConnection_BatteryUnit_DEREM_3p_6752.*_A_VA\[magnitude\]$'
    header_pattern_p3 = r'^PowerElectronicsConnection_BatteryUnit_DEREM_3p_6752.*_B_VA\[magnitude\]$'

    # Extract values using the header patterns
    p1 = context.first_parsed_output_df.filter(regex=header_pattern_p1, axis=1).iloc[row_index, 0]
    p2 = context.first_parsed_output_df.filter(regex=header_pattern_p2, axis=1).iloc[row_index, 0]
    p3 = context.first_parsed_output_df.filter(regex=header_pattern_p3, axis=1).iloc[row_index, 0]

    print("p1:", p1)
    print("p2:", p2)
    print("p3:", p3)
    assert (p1 != p2 or p2 != p3 or p1 != p3)


@when(u'The DER assignment process is called')
def step_impl(context):
    pass  # Done in environment.py


@then(u'The Assignment Lookup table should contain the name of each DER-EM')
def step_impl(context):
    # print(context.der_em_list)
    print(context.assignment_lookup_table)
    # print(context.association_lookup_table)
    for i in context.der_em_list:
        assert context.assignment_lookup_table[i]


@then(u'The Assignment Lookup Table should contain an mRID for each DER-EM')
def step_impl(context):
    for i in context.der_em_list:
        mrid = context.assignment_lookup_table[i]['mRID']
        assert type(mrid) is str
        assert len(mrid) == 37
        assert mrid[0] == '_'
        assert mrid[9] == '-'
        assert mrid[14] == '-'
        assert mrid[19] == '-'
        assert mrid[24] == '-'


@then(u'The mRID of each input in the Assignment Lookup Table should not be identical to any other input in the table.')
def step_impl(context):
    list_of_mrids = []
    for i in context.der_em_list:
        list_of_mrids.append(context.assignment_lookup_table[i]['mRID'])
    assert len(set(list_of_mrids)) == len(context.der_em_list)


@then(u'Each DER-EM name should be associated with a locational identifier in the Assignment Lookup Table.')
def step_impl(context):
    for i in context.der_em_list:
        assert context.assignment_lookup_table[i]['Bus']


@given(u'Grid services need to be dispatched')
def step_impl(context):
    assert path.exists(context.MEPath + "Outputs To DERMS/OutputtoGSP.xml") is True


@when(u'The GO dispatches a grid service request')
def step_impl(context):
    pass  # Done in environment.py


@then(u'The GO should output an XML file available for use by the GSP.')
def step_impl(context):
    assert path.exists(context.MEPath + "manually_posted_service_input.xml") is True


@given(u'A manually posted service input file is available')
def step_impl(context):
    assert path.exists(context.MEPath + "manually_posted_service_input.xml") is True


@when(u'The function to manually post a service is called')
def step_impl(context):
    assert ModelController.mcConfiguration.go_sensor_decision_making_manual_override is True


@then(u'A GOPostedService object should be instantiated')
def step_impl(context):
    assert context.posted_service_list is not False


@when(u'The EDMTimeKeeper on-timestep function is called')
def step_impl(context):
    pass  # Assumed, tests run in environment.py


@when(u'The EDMMeasurementProcessor measurement processing function is called')
def step_impl(context):
    pass  # Assumed, tests run in environment.py


@then(u'On-timestep updates should occur')
def step_impl(context):
    pass  # Assumed, tests run in environment.py


@then(u'New processed measurements should be available')
def step_impl(context):
    assert ModelController.edmMeasurementProcessor.get_current_measurements() is not None


@then(u'A new unified input request should be generated')
def step_impl(context):
    assert context.firstTPME1UIR


@then(u'The GOSensor should attempt to create a new GOPostedService object if applicable')
def step_impl(context):
    assert ModelController.goSensor.posted_service_list is not False


@then(u'GOOutputInterface should generate an output message')
def step_impl(context):
    assert path.exists(context.outputxmlpath) is True


@given(u'The EDMMeasurementProcessor has received at least one set of measurements.')
def step_impl(context):
    context.measurement_set = ModelController.edmMeasurementProcessor.get_current_measurements()


@then(u'The EDMMeasurementProcessor should provide measurements by a function call')
def step_impl(context):
    pass  # Completed in the Given step


@then(u'The measurements should have human-readable names (not mRIDs).')
def step_impl(context):
    for keys, values in context.measurement_set.items():
        if keys is not "Timestamp":
            assert values['Measurement name']


@when(u'The DER-S input processing method is called')
def step_impl(context):
    pass  # Performed in environment.py (by running the simulation)

@when(u'The GOSensor grid service request method is called')
def step_impl(context):
    pass  # Performed in environment.py (by running the simulation and providing a manual input xml)


@then(u'The unified input request should update')
def step_impl(context):
    print(context.firstTPME1UIR)
    assert context.firstTPME1UIR


@then(u'The logs should indicate a DER-S changed state from one timestep to the next.')
def step_impl(context):
    # Define the string to filter columns
    # Define the row index
    row_index = 1

    # Define the header pattern
    header_pattern = r'^PowerElectronicsConnection_BatteryUnit_DEREM_6344.*_A_VA\[magnitude\]$'

    # Use regular expression to find matching header
    print(context.first_parsed_output_df)
    matching_columns = context.first_parsed_output_df.filter(regex=header_pattern, axis=1)

    # Check if the matching column exists in the DataFrame
    if matching_columns.empty:
        assert matching_columns is not None
    else:
        # Get the value at the specified row_index and matching column
        column = matching_columns.iloc[:, 0]
        print("column:", column)
    v1 = column.iloc[5]
    v2 = column.iloc[6]
    print(column)
    print(v1)
    print(v2)
    assert (v1 != v2)


@then(u'The logs should indicate the DER-S updated at the right time in the input file.')
def step_impl(context):
    column = context.first_parsed_output_df.loc[:,"Timestamp"]
    print(column.iloc[6])
    assert column.iloc[6] == "2019-10-02 18:32:03"


@given(u'A ME simulation is running.')
def step_impl(context):
    pass  # Handled in environment.py. Full simulation run accomplishes this.


@when(u'A measurement timestep--three seconds-- elapses.')
def step_impl(context):
    pass  # Handled in environment.py. Full simulation run accomplishes this.


@then(
    u'Measurements are placed in a dictionary in the EDMMeasurementProcessor class, which are then printed to the '
    u'terminal by a test function.')
def step_impl(context):
    assert ModelController.edmMeasurementProcessor.current_measurements is not None
    assert type(ModelController.edmMeasurementProcessor.current_measurements) is dict


@when(u'The EDMTimeKeeper\'s on-timestep function is called')
def step_impl(context):
    context.first_timecode = int(ModelController.edmTimekeeper.sim_current_time)
    ModelController.edmTimekeeper.increment_sim_current_time()
    context.second_timecode = int(ModelController.edmTimekeeper.sim_current_time)


@then(u'Time is incremented by one second')
def step_impl(context):
    assert context.second_timecode == context.first_timecode + 1


@when(u'A DER-S calls the assignment function')
def step_impl(context):
    pass  # Performed in environment.py


@then(u'The DER association table contains keys for each input DER name')
def step_impl(context):
    # print(context.association_lookup_table)
    context.table_der_dict = {}
    for item in context.association_lookup_table:
        for key, value in item.items():
            context.table_der_dict[key] = value
    print(context.table_der_dict)
    for item in context.der_input_list:
        assert context.table_der_dict[item]


@then(u'The DER association table contains mRIDs associated with each name')
def step_impl(context):
    for item in context.der_input_list:
        mrid = context.table_der_dict[item]
        assert type(mrid) is str
        assert len(mrid) == 37
        assert mrid[0] == '_'
        assert mrid[9] == '-'
        assert mrid[14] == '-'
        assert mrid[19] == '-'
        assert mrid[24] == '-'

@given(u'GridAPPS-D is running')
def step_impl(context):
    pass  # Implemented in environment.py

@when(u'A SPARQL Query is sent to the database requesting a list of grid models')
def step_impl(context):
    context.list_of_model_names = [binding['feeder']['value'] for binding in context.list_of_models['data']['results']['bindings']]

@then(u'A list of grid models is returned.')
def step_impl(context):
    assert len(context.list_of_model_names) != 0
