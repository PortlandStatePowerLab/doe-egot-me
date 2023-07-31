import csv

# Constants
input_file = "df_test.csv"

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
