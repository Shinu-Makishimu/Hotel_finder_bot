from typing import Union, Dict, Any

import requests
import re
from database import get_settings
from loguru import logger
from settings import H_API_TOKEN


def make_locations_list(message) -> Union[dict[str, str], dict[str, Any]]:
    logger.info(f'function {make_locations_list.__name__} was called with arg {message.text}')
    data = request_locations(message)
    if not data:
        return {'bad_request': 'bad_request'}
    locations = dict()
    if len(data.get('suggestions')[0].get('entities')) > 0:
        for item in data.get('suggestions')[0].get('entities'):
            location_name = re.sub('<([^<>]*)>', '', item['caption'])
            locations[location_name] = item['destinationId']
        return locations



def request_locations(message):

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    language = get_settings(user_id=message.from_user.id, key='language')
    logger.info(f'function {request_locations.__name__} was called with message and use args: '
                f'lang: {language}\t text: {message.text}')

    querystring = {
        "query": message.text.strip(),
        "locale": language
    }
    # headers = {
    #     'x-rapidapi-host': "hotels4.p.rapidapi.com",
    #     'x-rapidapi-key': "163053c24amsh12466b55222e784p1eaa99jsn5c07d5ed2972"
    #     }
    #
    # при подстановке этого хедера апи токен читается не правильно и апи возвращает бэд реквест
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': H_API_TOKEN
        }

    response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
    data = response.json()
    return data


def delete_tags(html_text: Any) -> str:
    """
    функция удаления тегов из текста
    :param html_text:
    :return:
    """
    logger.info(f'function {delete_tags.__name__} was called')
    text = re.sub('<([^<>]*)>', '', html_text)
    return text


