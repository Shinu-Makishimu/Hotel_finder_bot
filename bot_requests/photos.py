import requests
import re
from database import get_settings
from loguru import logger
import json
from settings import API_TOKEN

# url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
#
# querystring = {"id":"1178275040"}
#
# headers = {
#     'x-rapidapi-host': "hotels4.p.rapidapi.com",
#     'x-rapidapi-key': "SIGN-UP-FOR-KEY"
#     }
#
# response = requests.request("GET", url, headers=headers, params=querystring)
#
# print(response.text)


def make_photo_list(hotel_id, counter) -> dict:
    logger.info(f'function {make_photo_list.__name__} was called')
    data = request_photos(hotel_id, counter)
    if not data:
        return {'bad_request': 'bad_request'}
    return data


def request_photos(hotel_id, counter):

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    logger.info(f'function {request_photos.__name__} was called with message and use args: '
                f'lang: {hotel_id}\t text: {counter}')

    querystring = {"id": hotel_id}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "163053c24amsh12466b55222e784p1eaa99jsn5c07d5ed2972"
        }
    # requests.request("GET", url, headers=headers, params=querystring)
    response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
    data = response.json()
    with open('photos_data.txt', 'w') as file:
        json.dump(data, file, indent=4)
    return data





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