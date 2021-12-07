import xmltodict
input_file = open("manually_posted_services.xml", "r")
data = input_file.read()
input_file.close()
data_dict=xmltodict.parse(data)
print(data_dict)

for item in data_dict["services"]:
    name = str(item)
    group_id = item["group_id"]
    service_type = item["service_type"]
    interval = item["interval"]
    power = item["power"]
    ramp = item["ramp"]
    price = item["price"]
    start_time = item["start_time"]