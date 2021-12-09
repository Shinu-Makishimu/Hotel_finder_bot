from datetime import datetime
import telebot
import re
import sqlite3
# TODO: переписать на sql

# памятка:
# user_id юзер id
# status положение в меню
# history история
# country страна
# currency валюта



user_status = {
    'new': 'first_use',
    'main': 'main menu',
    'sett': 'settings',
    'lowprice': 'low',
    'highprice': 'high',
    'bestdeal': 'diapason',
    'history': 'history user'
}


def check_user(message):
    """
    проверка наличия присутствия пользователя в бд. )
    :param message:
    :return:
    """

    user_id = message.from_user.id  # выделить пользовательский id из объекта сообщения
    connection = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute("SELECT user_id FROM clients WHERE user_id = {user_id}".format(user_id=user_id))
    response = cursor.fetchone()
    cursor.close()

    if response is None:
        return False
    else:
        return True


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
    # TODO: обернуть try - exept
    user_id = message.from_user.id  # выделить пользовательский id из объекта сообщения
    language = message.from_user.language_code  # выделить локализацию пользователя,
    currency = 'RUB'
    status = 'new'
    history = ''
    country = 'россия' # проверить в апи от отеля
    order = ''
    if language != 'ru':
        language = 'en'
        currency = 'EUR'
    connection = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = connection.cursor()
    request = """INSERT INTO clients VALUES ?,?,?,?,?,?,? """
    cursor.execute(
        request,
        (
            user_id,
            status,
            history,
            country,
            currency,
            language,
            order
        )
                   )
    connection.commit()
    cursor.close()



def set_navigate(message, value:str):
    """
    функция для изменения параметра навигации пользователя
    :param message:
    :param information:
    :return:
    """
    if not check_user(message):
        create_user(message)
    user_id = message.from_user.id
    connection = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = connection.cursor()
    request = """UPGRADE clients SET status= ? WHERE user_id = ?"""
    data = (value, user_id)
    cursor.execute(request, data)
    connection.commit()
    cursor.close()


def set_settings(user_id, key, value):
    connection = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = connection.cursor()
    request = ''
    if key == 'language':
        request = """UPGRADE clients SET language = ? FROM clients WHERE user_id = ?"""
    elif key == 'money':
        request = """UPGRADE clients SET currency = ? FROM clients WHERE user_id = ?"""
    data = (value, user_id)
    cursor.execute(request, data)
    connection.commit()
    cursor.close()



def get_navigate(message):
    """
    функция для возврата навигации пользователя
    или
    вернуть всё что сохранено
    :param message:
    :param all:
    :return:
    """
    user_id = message.from_user.id
    connection = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = connection.cursor()
    request = """SELECT status FROM clients WHERE user_id = ?"""
    cursor.execute(request, user_id)
    response = cursor.fetchone()
    cursor.close()
    return response

def get_settings(message):
    user_id = message.from_user.id
    connection = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT country, currency, language FROM clients WHERE user_id = {user_id}".format(user_id=user_id))
    response = cursor.fetchall()
    cursor.close()
    return response

def get_history(message):
    """
    возвращает историю пользователя

    :param message:
    :return:
    """
    response = 'История запросов отсутствует'
    user_id = message.from_user.id
    history = None
    # TODO: переписать метод формирования историии


