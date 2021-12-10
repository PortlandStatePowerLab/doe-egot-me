import xmltodict
from dict2xml import dict2xml
input_file = open("manually_posted_services.xml", "r")
data = input_file.read()
input_file.close()
data_dict=xmltodict.parse(data)
print(data_dict)
service_messages = []

for key, item in data_dict["services"].items():
    print(item)
    name = str(key)
    group_id = item["group_id"]
    service_type = item["service_type"]
    interval_start = item["interval_start"]
    interval_duration = item["interval_duration"]
    power = item["power"]
    ramp = item["ramp"]
    price = item["price"]
    start_time = item["start_time"]
    service_message_data = {
        "service_name": name,
        "group_id": group_id,
        "service_type": service_type,
        "interval_start": interval_start,
        "interval_duration": interval_duration,
        "power": power,
        "ramp": ramp,
        "price": price
    }
    service_messages.append(service_message_data)

print(service_messages)

x = dict2xml(service_messages)
print(x)
print(type(x))
xmlfile = open("toGSP.xml", "w")
xmlfile.write(x)
xmlfile.close()