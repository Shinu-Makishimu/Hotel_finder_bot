import json
import re
from typing import Any, Union

import requests
from loguru import logger

from accessory import get_date
from bot_requests.photos import make_photo_list
from database import get_settings
from language import interface
from settings import API_TOKEN

# памятка
# querystring
#         {
#                 "destinationId":"1506246"
#                 ,"pageNumber":"1",
#                 "pageSize":"25",
#                 "checkIn":"2020-01-08",
#                 "checkOut":"2020-01-15",
#                 "adults1":"1",
#                 "sortOrder":"PRICE",
#                 "locale":"en_US",
#                 "currency":"USD"
#         }
# parameters:
#         {
#             'language': 'ru_RU',
#             'currency': 'RUB',
#             'status': 'old',
#             'first_name': 'Kelbor',
#             'last_name': 'Hal',
#             'command': 'lowprice',
#             'city': '11594',
#             'hotel_count': '12',
#             'photo_count': '2',
#             'date1': '1632258000.0',
#             'date2': '1703710800.0'
#         }


order = {
    'lowprice': 'PRICE',
    'highprice': 'PRICE_HIGHEST_FIRST',
    'bestdeal': 'DISTANCE_FROM_LANDMARK'
}


# noinspection PyTypeChecker
def get_hotels(user_id:str) -> dict:
    """
    Функция получает юзер айди, на его основе формирует с помощью вспомогательных функций список результатов
    :param user_id:
    :return: если сайт вернул bad request, возвращает bad request, если результата нет, none
     иначе словарь с результатами
    """

    logger.info(f'function {get_hotels.__name__} was called with user_id {user_id}')
    params = get_settings(user_id=user_id, key='all')

    data = request_hotels(p=params)
    if 'bad_req' in data:
        return ['bad_request']

    data = structure_hotels_info(user_id=user_id, data=data)

    if not data or len(data['results']) < 1:
        return None
    if params['command'] == 'bestdeal':
        next_page = data.get('next_page')
        distance = float(params['distance'])
        while next_page and next_page < 5 \
                and float(data['results'][-1]['distance'].replace(',', '.').split()[0]) <= distance:
            add_data = request_hotels(p=params, page=next_page)
            if 'bad_req' in data:
                logger.warning('bad_request')
                break
            add_data = structure_hotels_info(user_id=user_id, data=add_data)
            if add_data and len(add_data["results"]) > 0:
                data['results'].extend(add_data['results'])
                next_page = add_data['next_page']
            else:
                break
        max_hotels_numbers = int(params['quantity'])
        data = choose_best_hotels(hotels=data['results'], distance=distance, limit=max_hotels_numbers)
    else:
        data = data['results']

    data = generate_hotels_descriptions(hotels=data, user_id=user_id)
    return data


def request_hotels(p, page=1):
    """
    функция запроса списка отелей из апи

    почему то при использовании API_TOKEN, апи не принимает его. корректность в енв проверено
    :param p:
    :param page:
    :return:
    """
    logger.info(f'Function {request_hotels.__name__} called with argument: parameters = {p}')
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {
        "destinationId": p['city'],
        "pageNumber": str(page),
        "pageSize": p['hotel_count'],
        "checkIn": get_date(p['date1']),
        "checkOut": get_date(p['date2']),
        "adults1": "1",
        "sortOrder": order[p['command']],
        "locale": p['language'],
        "currency": p['currency']
    }

    if p['command'] == 'bestdeal':
        querystring['priceMax'] = p['max_price']
        querystring['priceMin'] = p['min_price']
        querystring['pageSize'] = '25'

    logger.info(f'Search parameters: {querystring}')

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "163053c24amsh12466b55222e784p1eaa99jsn5c07d5ed2972"
        # 'x-rapidapi-key': API_TOKEN
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        data = response.json()
        if data.get('message'):
            raise requests.exceptions.RequestException
        # with open('hotels_data.txt', 'w') as file: # just for testing
        #     json.dump(data, file, indent=4)
        logger.info(f'Hotels api(properties/list) response received: {data}')
        return data

    except requests.exceptions.RequestException as e:
        logger.error(f'Error receiving response: {e}')
        return {'bad_req': 'bad_req'}


def structure_hotels_info(user_id, data) -> dict:
    """
    Структурирование результатов поиск для удобной обработки в дальнейшем
    :param user_id:
    :param data:
    :return:
    """
    logger.info(f'Function {structure_hotels_info.__name__} called with args user_id = {user_id}, data = {data}')
    data = data.get('data', {}).get('body', {}).get('searchResults')
    hotels = dict()
    hotels['total_count'] = data.get('totalCount', 0)

    logger.info(f"Next page: {data.get('pagination', {}).get('nextPageNumber', 0)}")
    hotels['next_page'] = data.get('pagination', {}).get('nextPageNumber')
    hotels['results'] = []

    if hotels['total_count'] > 0:
        for i_hotel in data.get('results'):
            hotel = dict()
            hotel['name'] = i_hotel.get('name')
            hotel['id'] = i_hotel.get('id')
            hotel['star_rating'] = i_hotel.get('starRating', 0)
            hotel['price'] = hotel_price(i_hotel)
            if not hotel['price']:
                continue
            hotel['distance'] = i_hotel.get('landmarks')[0].get(
                'distance',
                interface['errors']['no_information'][get_settings(user_id=user_id, key='language')]
            )
            hotel['address'] = hotel_address(i_hotel, user_id=user_id)

            if hotel not in hotels['results']:
                hotels['results'].append(hotel)
        logger.info(f'Hotels in function {structure_hotels_info.__name__}: {hotels}')
        return hotels


def choose_best_hotels(hotels: list[dict], distance: float, limit: int) -> list[dict]:
    logger.info(f'Function {choose_best_hotels.__name__} called with arguments: '
                f'distance = {distance}, quantity = {limit}\n{hotels}')
    hotels = list(filter(lambda x: float(x["distance"].strip().replace(',', '.').split()[0]) <= distance, hotels))
    logger.info(f'Hotels filtered: {hotels}')
    hotels = sorted(hotels, key=lambda x: x["price"])
    logger.info(f'Hotels sorted: {hotels}')
    if len(hotels) > limit:
        hotels = hotels[:limit]
    return hotels


def generate_hotels_descriptions(hotels: dict, user_id: str) -> dict[Any, dict[str, Union[str, list[str]]]]:
    """
    формирование словаря с результатами поиска. словарь вида:
    hotels_info =
                {
                    "hotel_ID":
                        {
                            "photo": список изображений
                            "message": сформированный ответ для пользователя
                        }
                }

    :param hotels:
    :param user_id:
    :return:
    """
    logger.info(f'Function {generate_hotels_descriptions.__name__} called with argument {hotels}')
    hotels_info = dict()
    # hotels_info = []
    photo_number = get_settings(user_id=user_id, key='photo_count')
    for hotel in hotels:
        photo = make_photo_list(hotel_id=hotel.get('id'), counter=int(photo_number))
        message = (
            f"{interface['elements']['hotel'][get_settings(user_id=user_id, key='language')]}: "
            f"{hotel.get('name')}\n"

            f"{interface['elements']['rating'][get_settings(user_id=user_id, key='language')]}: "
            f"{hotel_rating(rating=hotel.get('star_rating'), user_id=user_id)}\n"

            f"{interface['elements']['price'][get_settings(user_id=user_id, key='language')]}: "
            f"{hotel['price']} {get_settings(user_id=user_id, key='currency')}\n"

            f"{interface['elements']['distance'][get_settings(user_id=user_id, key='language')]}: "
            f"{hotel.get('distance')}\n"

            f"{interface['elements']['address'][get_settings(user_id=user_id, key='language')]}: "
            f"{hotel.get('address')}\n"
        )

        hotels_info.update(
            {
                hotel.get('name'):
                    {
                        "message": message,
                        "photo": photo
                    }
            })

    return hotels_info


def hotel_price(hotel) -> int:
    logger.info(f'Function {hotel_price.__name__} called with argument {hotel}')
    price = 0
    if hotel.get('ratePlan').get('price').get('exactCurrent'):
        price = hotel.get('ratePlan').get('price').get('exactCurrent')
    else:
        price = hotel.get('ratePlan').get('price').get('current')
        price = int(re.sub(r'[^0-9]', '', price))
    return price


def hotel_address(hotel: dict, user_id: str) -> str:
    logger.info(f'Function {hotel_address.__name__} called with argument {hotel}')
    message = interface['errors']['no_information'][get_settings(user_id=user_id, key='language')]
    if hotel.get('address'):
        message = hotel.get('address').get('streetAddress', message)
    return message


def hotel_rating(rating: float, user_id: str) -> str:
    logger.info(f'Function {hotel_rating.__name__} called with {rating}')
    if not rating:
        return interface['errors']['no_information'][get_settings(user_id=user_id, key='language')]
    return '⭐' * int(rating)
