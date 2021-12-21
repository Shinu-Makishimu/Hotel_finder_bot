import requests
import re
from database import get_settings
from loguru import logger

import json
from settings import API_TOKEN, PHOTO_SIZE

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


def make_photo_list(hotel_id:str, counter:int) -> list[str]:
    logger.info(f'function {make_photo_list.__name__} was called')
    data = request_photos(hotel_id, counter)
    if not data:
        return ['bad_request']
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

    response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
    data = response.json()
    photo_list = list()
    for i_index, i_photo in enumerate(data['hotelImages']):
        if i_index == counter:
            break
        photo_list.append(i_photo['baseUrl'].replace("{size}", PHOTO_SIZE))

    return photo_list



#
#
#
# for i_hotel in json_data:
#     print(i_hotel['hotelId'])
#     for i_index, i_photo in enumerate(i_hotel['hotelImages']):
#         if i_index == limit:
#             break
#         url = i_photo['baseUrl'].replace("{size}", )
#         print(url)




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