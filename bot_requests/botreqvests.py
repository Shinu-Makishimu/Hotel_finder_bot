import requests
import json
url = "https://hotels4.p.rapidapi.com/locations/v2/search"

querystring = {"query":"new york","locale":"en_US","currency":"USD"}

headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': "163053c24amsh12466b55222e784p1eaa99jsn5c07d5ed2972"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

data = json.loads(response.text)

with open('exmlpe_call.txt', 'w') as file:
    json.dump(data, file, indent=4)

