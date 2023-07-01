import requests

# response = requests.get('http://localhost:8000')
# print(response)


data = {'param1': 'value1', 'param2': 'value2'}

response = requests.post('https://localhost:8000', data=data)
print(response.text)