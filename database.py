import sqlite3
import datetime
import redis
import re
from accessory import get_timestamp, get_date
from settings import NAME_DATABASE

redis_db = redis.StrictRedis(host='localhost', port=6379, db=1, charset='utf-8', decode_responses=True)


# секция хорошего, годного sqlite3
def create_bd_if_not_exist():
    with sqlite3.connect(NAME_DATABASE) as db:
        cursor = db.cursor()

        query = """PRAGMA foreign_keys=on;"""
        query_1 = """CREATE TABLE IF NOT EXISTS clients(
        user_id INTEGER PRIMARY KEY NOT NULL,
        language TEXT,
        currency TEXT,
        status TEXT,
        FOREIGN KEY (user_id) REFERENCES requests (user_id)
        );"""
        query_2 = """CREATE TABLE IF NOT EXISTS requests(
        user_id INTEGER PRIMARY KEY NOT NULL,
        command TEXT,
        price TEXT,
        city TEXT,
        hotel_count TEXT,
        photo_count INTEGER,
        date REAL,
        hotels TEXT);"""

        cursor.execute(query)
        cursor.execute(query_2)
        cursor.execute(query_1)
        db.commit()


def create_user_in_db(message):
    user_id = message.from_user.id  # выделить пользовательский id из объекта сообщения
    language = message.from_user.language_code  # выделить локализацию пользователя,
    currency = 'RUB'
    status = 'new'
    if language != 'ru':
        language = 'en'
        currency = 'EUR'
    with sqlite3.connect(NAME_DATABASE) as db:
        cursor = db.cursor()
        request = """INSERT INTO clients VALUES (?,?,?,?) """
        cursor.execute(
            request,
            (
                user_id,
                language,
                currency,
                status
            )
        )
        db.commit()


def check_user_in_db(message):
    """
    проверка наличия присутствия пользователя в бд. )
    :param message:
    :return:
    """

    user_id = message.from_user.id  # выделить пользовательский id из объекта сообщения

    with sqlite3.connect(NAME_DATABASE, check_same_thread=False) as db:
        cursor = db.cursor()
        cursor.execute("""SELECT user_id FROM clients WHERE user_id=:user_id""", {'user_id': user_id})
        response = cursor.fetchone()

    if response is None:
        return False
    else:
        return True


def get_user_from_bd(message):
    user_id = message.from_user.id

    with sqlite3.connect(NAME_DATABASE) as db:
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM clients WHERE user_id=:user_id""",
                       {'user_id': user_id})
        response = cursor.fetchall()
        return response[0]


def set_settings_in_db(user_id, key, value):
    with sqlite3.connect(NAME_DATABASE, check_same_thread=False) as db:
        cursor = db.cursor()
        request = ''
        if key == 'language':
            request = """UPDATE clients SET language = ? WHERE user_id = ?"""
        elif key == 'currency':
            request = """UPDATE clients SET currency = ? WHERE user_id = ?"""
        elif key == 'status':
            request = """UPDATE clients SET key = ? WHERE user_id = ?"""

        data = (value, user_id)
        cursor.execute(request, data)
        db.commit()


# секция shit-redis


def check_user_in_redis(msg):
    """
    проверка наличия присутствия пользователя.
    сначала проверяем в редисе, если в редисе нет, проверяем в sqlite. если в sqlite нет, то создаём пользователя
    и загружаем его в редис
    :param message:
    :return:
    """

    user_id = msg.from_user.id
    result_in_redis = redis_db.hget(user_id, 'status')  # если ключа нет, вернёт нан
    date = str(datetime.datetime.now().date()).split('-')
    y, m, d = date

    if result_in_redis is None:
        if not check_user_in_db(msg):
            create_user_in_db(msg)
        user_id, language, currency, status = get_user_from_bd(msg)
        redis_db.hset(user_id, mapping={'language': language})
        redis_db.hset(user_id, mapping={'currency': currency})
        redis_db.hset(user_id, mapping={'status': status})
        redis_db.hset(user_id, mapping={'city': ''})
        redis_db.hset(user_id, mapping={'hotel_count': ''})
        redis_db.hset(user_id, mapping={'photo_count': ''})
        redis_db.hset(user_id, mapping={'order': ''})
        redis_db.hset(user_id, mapping={'date': get_timestamp(y, m, d)})


def set_settings(msg, key, value):
    user_id = msg.from_user.id
    check_user_in_redis(msg)

    if key == 'language':
        set_settings_in_db(user_id, key, value)
        redis_db.hset(user_id, mapping={'language': value})
    elif key == 'currency':
        set_settings_in_db(user_id, key, value)
        redis_db.hset(user_id, mapping={'currency': value})
    elif key == 'status':
        set_settings_in_db(user_id, key, value)
        redis_db.hset(user_id, mapping={'status': value})
    elif key == 'city':
        redis_db.hset(user_id, mapping={'city': value})
    elif key == 'hotel_count':
        redis_db.hset(user_id, mapping={'hotel_count': value})
    elif key == 'photo_count':
        redis_db.hset(user_id, mapping={'photo_count': value})
    elif key == 'order':
        redis_db.hset(user_id, mapping={'order': value})





def get_settings(msg, key=False):
    user_id = msg.from_user.id
    check_user_in_redis(msg)
    result = \
        {
            'language': re.search(r'\w+', str(redis_db.hget(user_id, 'language'))[2:])[0],
            'currency': re.search(r'\w+', str(redis_db.hget(user_id, 'currency'))[2:])[0],
            'status': re.search(r'\w+', str(redis_db.hget(user_id, 'status'))[2:])[0],
            'city': re.search(r'\w+', str(redis_db.hget(user_id, 'city'))[2:])[0],
            'hotel_count': re.search(r'\w+', str(redis_db.hget(user_id, 'hotel_count'))[2:])[0],
            'photo_count': re.search(r'\w+', str(redis_db.hget(user_id, 'photo_count'))[2:])[0],
            'order': re.search(r'\w+', str(redis_db.hget(user_id, 'order'))[2:])[0],
        }
    if key and key in result.keys():
        return result[key]
    return result


def set_navigate(msg, value):

    check_user_in_redis(msg)

    user_id = msg.from_user.id

    redis_db.hset(user_id, mapping={'status': value})


def get_navigate(msg):
    check_user_in_redis(msg)

    user_id = msg.from_user.id
    result = redis_db.hget(user_id, 'status')
    return re.search(r'\w+', str(result)[2:])[0]


def set_history(user_id):
    pass


def get_history(user_id):
    pass


#################################################################################
# some buffer


# def load_user_in_redis(msg):
#     user_id = msg.from_user.id
#
#     if not check_user_in_redis(msg):
#         if not check_user_in_db(msg):
#             create_user_in_db(msg)
#         user_id, language, currency, status = get_user_from_bd(msg)
#         redis_db.hset(user_id, mapping={'language': language})
#         redis_db.hset(user_id, mapping={'currency': currency})
#         redis_db.hset(user_id, mapping={'status': 'new'})
#         redis_db.hset(user_id, mapping={'city': ''})
#         redis_db.hset(user_id, mapping={'hotel_count': ''})
#         redis_db.hset(user_id, mapping={'photo_count': ''})
#         redis_db.hset(user_id, mapping={'photo_count': ''})
#     else:

# def get_settings_old(msg, key=False):
#     user_id = msg.from_user.id
#     check_user_in_redis(msg)
#
#     if not key:
#         return redis_db.hgetall(user_id)
#     else:
#         result = False
#         if key == 'language':
#             result = redis_db.hget(user_id, 'language')
#         elif key == 'currency':
#             result = redis_db.hget(user_id, 'currency')
#         elif key == 'status':
#             result = redis_db.hget(user_id, 'status')
#         elif key == 'city':
#             result = redis_db.hget(user_id, 'city')
#         elif key == 'hotel_count':
#             result = redis_db.hget(user_id, 'hotel_count')
#         elif key == 'photo_count':
#             result = redis_db.hget(user_id, 'photo_count')
#         elif key == 'order':
#             result = redis_db.hget(user_id, 'order')
#         return re.search(r'\w+', str(result)[2:])[0]
# ##            create_user_in_db(message)
# user_id, language, currency, status = get_user_from_bd(message)


# def create_user(message):
#     """
#      hset(self, name, key=None, value=None, mapping=None)
#      |      Set ``key`` to ``value`` within hash ``name``,
#      |      ``mapping`` accepts a dict of key/value pairs that will be
#      |      added to hash ``name``.
#      |      Returns the number of fields that were added.
#     :param message:
#     :return:
#     language -язык пользователя
#     status - флаг активной сессии
#     history списко с запросами
#     """
#     user_id = message.from_user.id  # выделить пользовательский id из объекта сообщения
#     language = message.from_user.language_code  # выделить локализацию пользователя,
#     money = 'RUB'
#     if language != 'ru':
#         language = 'en'
#         money = 'EUR'
#     redis_db.hset(user_id, mapping={'language': language})
#     redis_db.hset(user_id, mapping={'money': money})
#     redis_db.hset(user_id, mapping={'status': 'new'})
#     redis_db.hset(user_id, mapping={'city': ''})
#     redis_db.hset(user_id, mapping={'hotel_count': ''})
#     redis_db.hset(user_id, mapping={'photo_count': ''})
#     redis_db.hset(user_id, mapping={'photo_count': ''})
#
#
#
# def set_navigate(message, value):
#     """
#     функция для изменения параметра навигации пользователя
#     :param message:
#     :param information:
#     :return:
#     """
#     user_id = message.from_user.id
#
#     if not check_user(message):
#         create_user(message)
#     redis_db.hset(user_id, mapping={'status': value})
#
#
# def get_navigate(message, all=False):
#     """
#     функция для возврата навигации пользователя
#     или
#     вернуть всё что сохранено
#     :param message:
#     :param all:
#     :return:
#     """
#     user_id = message.from_user.id
#     if not check_user(message):
#         create_user(message)
#     if not all:
#         result = redis_db.hget(user_id, 'status')
#         return re.search(r'\w+', str(result)[2:])[0]
#     else:
#         return redis_db.hgetall(user_id)

# def set_navigate(message, value:str):
#     """
#     функция для изменения параметра навигации пользователя
#     :param message:
#     :param information:
#     :return:
#     """
#     if not check_user(message):
#         create_user(message)
#     user_id = message.from_user.id
#     with sqlite3.connect('bot.db', check_same_thread=False) as db:
#         cursor = db.cursor()
#         request = """UPDATE clients SET status = ? WHERE user_id = ?"""
#         data = (value, user_id)
#         cursor.execute(request, data)
#         db.commit()
#
#
# def get_navigate(message):
#     """
#     функция для возврата навигации пользователя
#     или
#     вернуть всё что сохранено
#     :param message:
#     :param all:
#     :return:
#     """
#     user_id = message.from_user.id
#     with sqlite3.connect('bot.db', check_same_thread=False) as db:
#         cursor = db.cursor()
#         cursor.execute("""SELECT status FROM clients WHERE user_id=:user_id""", {'user_id': user_id})
#         response = cursor.fetchone()
#         return response[0]
#
# def set_session_inf(user_id, key, value):
#
#     with sqlite3.connect('bot.db', check_same_thread=False) as db:
#     cursor = db.cursor()
#     request = ''
#     if key == 'language':
#         request = """UPDATE clients SET language = ? WHERE user_id = ?"""
#     elif key == 'money':
#         request = """UPDATE clients SET currency = ? WHERE user_id = ?"""
#     elif key == 'order':
#         request = """INSERT INTO requests SET price = ? date = ? WHERE user_id = ?"""
#         data = value, ge


# # добавим запись в таблицу запись о пользователе
# user_id = 999999
# language = 'ru'
# currency = 'RUB'
# status = 'new'
# with sqlite3.connect('new_test.db') as db:
#     cursor = db.cursor()
#     request = """INSERT INTO clients VALUES (?,?,?,?) """
#     cursor.execute(
#         request,
#         (
#             user_id,
#             status,
#             currency,
#             language,
#         )
#     )

#
# if __name__ == 'database_v1':
#     user_id = 999999
#     language = 'ru'
#     currency = 'RUB'
#     status = 'new'
#     insert_data = [
#         (999999, 'lowprice'),
#         (999999, 'выборг'),
#         (999999, '20'),
#         (999999, '3'),
#         (999999, get_timestamp(2021, 3, 3)),
#         (999999, 'ссылка на отель1;ссылка на отель2;ссылка на отель3')
#     ]
#
#     with sqlite3.connect('new_test.db') as db:
#         cursor = db.cursor()
#         request = """UPDATE requests SET command = ? WHERE user_id = ?"""
#         request_1 = """UPDATE requests SET command = ? WHERE user_id = ?"""
#         request_2 = """UPDATE requests SET command = ? WHERE user_id = ?"""
#         request_3 = """UPDATE requests SET command = ? WHERE user_id = ?"""
#         request_4 = """UPDATE requests SET command = ? WHERE user_id = ?"""
#         request_5 = """UPDATE requests SET command = ? WHERE user_id = ?"""
#         request_6 = """UPDATE requests SET command = ? WHERE user_id = ?"""
#
#     #     user_id INTEGER PRIMARY KEY NOT NULL,
#     #     command TEXT,
#     #     price TEXT,
#     #     city TEXT,
#     #     hotel_count TEXT,
#     #     photo_count INTEGER,
#     #     date REAL,
#     #     hotels TEXT);"""

######################################################################################
# redis, shit


#
#
#
