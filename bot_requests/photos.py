import requests
from loguru import logger

from settings import PHOTO_SIZE, H_API_TOKEN


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


def make_photo_list(hotel_id:str, counter: int) -> list[str]:
    """
    Функция формирует список ссылок на фото отеля
    :param hotel_id:
    :param counter:
    :return:
    """
    logger.info(f'function {make_photo_list.__name__} was called')
    if counter == 0:
        return []
    data = request_photos(hotel_id, counter)
    if not data:
        return ['bad_request']
    return data


def request_photos(hotel_id, counter):
    """
    функция запрашивает у апи фотографии
    :param hotel_id:
    :param counter:
    :return:
    """
    logger.info(f'function {request_photos.__name__} was called with message and use args: '
                f'lang: {hotel_id}\t text: {counter}')

    photo_list = list()
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": hotel_id}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': H_API_TOKEN
        }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=40)
        data = response.json()
        logger.info(f'function {request_photos.__name__} get {data}')
        for i_index, i_photo in enumerate(data['hotelImages']):
            if i_index == counter:
                break
            photo_list.append(i_photo['baseUrl'].replace("{size}", PHOTO_SIZE))
    except requests.exceptions.ReadTimeout as error:
        logger.error(f'Function {request_photos.__name__} was crushed with error {error} ')

    return photo_list


