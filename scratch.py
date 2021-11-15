import os
file_path = r"C:/Users/stant/PycharmProjects/doe-egot-me/RWHDERS Inputs/"
filename_list = os.listdir(file_path)
parsed_filename_list = []
for i in filename_list:
    g = i.split('_')
    g[0] = g[0][-5:]
    g[1] = g[1][3:6]
    parsed_filename_list.append({g[0]: {"Filepath":i, "Bus":g[1]}})
    # print(parsed_filename_list)
    input_dict = {}
    for d in parsed_filename_list:
        input_dict.update(d)
    # print(input_dict)


for key, value in input_dict.items():
    print(key)
    print(value)
    print(file_path + value['Filepath'])
    import csv
    with open(file_path + value['Filepath'], newline='') as csvfile:
        der_input_reader = csv.reader(csvfile)
        for row in der_input_reader:
            current_der_input = {row[0]: row[1]}
            print(current_der_input)
    current_der_real_power = current_der_input['P']
    current_der_input_request = {key, current_der_real_power}
    print(current_der_input_request)