from datetime import datetime
import telebot

import redis

redis_db = redis.StrictRedis(host='localhost', port=6379, db=1, charset='utf-8', decode_responses=True)

user_status = {
    None: 'first_use',
    0: 'start',
    1: 'settings',
    2: 'country',
    3: 'city',
    4: 'radius',
    5: 'price'
}

def check_user(message):
    """
    проверка наличия присутствия пользователя в бд. )
    :param message:
    :return:
    """
    user_id = message.from_user.id  # выделить пользовательский id из объекта сообщения
    result = redis_db.hget(user_id, 'status')  # если ключа нет, вернёт нан
    return result


def create_user(message):
    """
     hset(self, name, key=None, value=None, mapping=None)
     |      Set ``key`` to ``value`` within hash ``name``,
     |      ``mapping`` accepts a dict of key/value pairs that will be
     |      added to hash ``name``.
     |      Returns the number of fields that were added.
    :param message:
    :return:
    language -язык пользователя
    status - флаг активной сессии
    history списко с запросами
    """
    user_id = message.from_user.id  # выделить пользовательский id из объекта сообщения
    language = message.from_user.language_code  # выделить локализацию пользователя,
    if language != 'ru':
        language = 'en'
    redis_db.hset(user_id, mapping={'language': language, 'money':  '', 'status': None, 'history': list()})


def add_information(message, information):
    """
    добавить нестандартную информацию пользователю (а надо ли)
    :param message:
    :param information:
    :return:
    """
    if not check_user(message):
        create_user(message)
    user_id = message.from_user.id
    redis_db.hset(user_id, {'other': information})


def return_history(message):
    """
    возвращает историю пользователя

    :param message:
    :return:
    """
    response = 'История запросов отсутствует'
    user_id = message.from_user.id
    history = redis_db.hget(user_id, 'history')
    if len(history) == 0:
        return response
    else:
        response = 'История\n'
        for i_line in history:
            response += i_line + '\n'
    return response


