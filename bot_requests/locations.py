import re
import requests
from telebot import types
from typing import Dict, Any

from loguru import logger
from settings import H_API_TOKEN
from database import get_settings


def make_locations_list(message: types.Message) -> Dict:
    """
    Функция, формирующая словарь локаций, для формирования клавиатуры локаций
    :param message: сообщение, полученное от пользователя.
    :return: словарь локаций, полученных в результате запроса к api
    """
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


def request_locations(message: types.Message) -> Dict:
    """
    Функция осуществляет запрос к API
    :param message: сообщение пользователя
    :return: словарь результатов
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    language = get_settings(user_id=message.from_user.id, key='language')
    logger.info(f'function {request_locations.__name__} was called with message and use args: '
                f'lang: {language}\t text: {message.text}')

    querystring = {
        "query": message.text.strip(),
        "locale": language
    }

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
    :param html_text: строка с тегами
    :return: строка без тегов
    """
    logger.info(f'function {delete_tags.__name__} was called')
    text = re.sub('<([^<>]*)>', '', html_text)
    return text
