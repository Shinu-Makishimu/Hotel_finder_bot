import requests
import re
from database import get_settings
from settings import API_TOKEN


def make_locations_list(message) -> dict:

    data = request_locations(message)
    print(data)
    if not data:
        return {'bad_request': 'bad_request'}
    locations = dict()
    if len(data.get('suggestions')[0].get('entities')) > 0:
        for item in data.get('suggestions')[0].get('entities'):
            location_name = re.sub('<([^<>]*)>', '',item['caption'])
            locations[location_name] = item['destinationId']
        return locations



def request_locations(message):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    language = get_settings(message, 'language')

    if language != 'ru':
        language = 'en_US'
    else:
        language= 'ru_RU'
    querystring = {
        "query": message.text.strip(),
        "locale": language
    }
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "163053c24amsh12466b55222e784p1eaa99jsn5c07d5ed2972"
        }
    #

    # headers = {
    #     'x-rapidapi-host': "hotels4.p.rapidapi.com",
    #     'x-rapidapi-key': API_TOKEN
    #     }

    response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
    data = response.json()
    # подумать что делать  если нету ничего в ответе
    return data


def delete_tags(html_text):
    text = re.sub('<([^<>]*)>', '', html_text)
    return text






##################################################################################
# import json
# url = "https://hotels4.p.rapidapi.com/locations/v2/search"
#
# querystring = {"query":"new york","locale":"en_US","currency":"USD"}
#
# headers = {
#     'x-rapidapi-host': "hotels4.p.rapidapi.com",
#     'x-rapidapi-key': "163053c24amsh12466b55222e784p1eaa99jsn5c07d5ed2972"
#     }
#
# response = requests.request("GET", url, headers=headers, params=querystring)
#
# data = json.loads(response.text)
#
# with open('exmlpe_call.txt', 'w') as file:
#     json.dump(data, file, indent=4)
#

# url = "https://hotels4.p.rapidapi.com/locations/v2/search"
#
# querystring = {"query":"new york","locale":"en_US","currency":"USD"}
#
# headers = {
#     'x-rapidapi-host': "hotels4.p.rapidapi.com",
#     'x-rapidapi-key': "163053c24amsh12466b55222e784p1eaa99jsn5c07d5ed2972"
#     }
#
# response = requests.request("GET", url, headers=headers, params=querystring)
#
# print(response.text)