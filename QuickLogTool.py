import csv
import re
from datetime import datetime

def read_csv_file(file_path):
    data = []
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def get_matching_columns(data, regex_pattern):
    column_names = data[0].keys()
    matching_columns = [col for col in column_names if re.search(regex_pattern, col)]
    return matching_columns

def convert_to_unix_timestamp(datetime_str, date_format="%Y-%m-%d %H:%M:%S"):
    dt_object = datetime.strptime(datetime_str, date_format)
    unix_timestamp = int(dt_object.timestamp())
    return unix_timestamp

def print_column_contents(data, column_name1, column_names):
    col1_values = [row[column_name1] for row in data]

    print(f"Contents of '{column_name1}' column (Unix timestamps):")
    for value in col1_values:
        unix_timestamp = convert_to_unix_timestamp(value)
        print(unix_timestamp)

    print("\nMatching columns:")
    for column in column_names:
        col_values = [row[column] for row in data]
        print(f"\nContents of '{column}' column:")
        for value in col_values:
            print(value)

if __name__ == "__main__":
    file_path = "/root/PycharmProjects/doe-egot-me/Logged Grid State Data/MeasOutputLogs_23_07_2023_10_43.csv"
    try:
        data = read_csv_file(file_path)
        column_names = get_matching_columns(data, r'DEREM_6341')

        print("\nAvailable column names:")
        print(", ".join(column_names))

        column_name1 = "Timestamp"

        if column_name1 in data[0].keys() and column_names:
            print_column_contents(data, column_name1, column_names)
        else:
            print("Error: Invalid column names or no matching columns found.")
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'. Please provide a valid file path.")
    except Exception as e:
        print(f"An error occurred: {e}")
