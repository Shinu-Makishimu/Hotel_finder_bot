import requests
from typing import List
from loguru import logger

from settings import PHOTO_SIZE, H_API_TOKEN


def make_photo_list(hotel_id: str, counter: int) -> List[str]:
    """
    Функция формирует список ссылок на фото отеля
    :param hotel_id: id отеля
    :param counter: счетчик фотографий
    :return: список со ссылками на фотографии
    """
    logger.info(f'function {make_photo_list.__name__} was called')
    if counter == 0:
        return []
    data = request_photos(hotel_id, counter)
    if not data:
        return ['bad_request']
    return data


def request_photos(hotel_id, counter) -> List or None:
    """
    функция запрашивает у апи фотографии
    :param hotel_id: id отеля
    :param counter: счетчик фотографий
    :return:возвращает список фотографий или none если запрос не удался
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
        return None
    return photo_list


