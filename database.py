import sqlite3
import datetime
import re
from accessory import get_timestamp, get_date
from settings import NAME_DATABASE, redis_db
from loguru import logger


#
# памятка состояний навигации
# new новый нюфаг
# old олдфаг
# main главное меню
# sett настройки
# history история
# city_h город поиска
# count_h количество результатов в выдаче
# count_p количество фото в одной выдаче
# calendar очередь показывать календарь
#
#
#

language_dict= {
    'ru': 'ru_RU',
    'en': 'en_US'
}
#################################### секция sqlite3 ####################################


def create_bd_if_not_exist():
    logger.info(f'Function {create_bd_if_not_exist.__name__} called')
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
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


def create_user_in_db(user_id, language):
    logger.info(f'Function {create_user_in_db.__name__} called and use args: user_id{user_id}\tlang {language}')
    currency = 'RUB'
    status = 'new'
    if language != 'ru_RU':
        language = 'en_US'
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


def check_user_in_db(user_id):
    """
    проверка наличия присутствия пользователя в бд. )
    :param message:
    :return:
    """

    logger.info(f'Function {check_user_in_db.__name__} called and use args: user_id\t{user_id}')

    with sqlite3.connect(NAME_DATABASE, check_same_thread=False) as db:
        cursor = db.cursor()
        cursor.execute("""SELECT user_id FROM clients WHERE user_id=:user_id""", {'user_id': user_id})
        response = cursor.fetchone()

    if response is None:
        logger.info(f"user wasn't found in sqlite")
        return False
    else:
        logger.info(f"user was found in sqlite")
        return True


def get_user_from_bd(user_id):
    logger.info(f'Function {get_user_from_bd.__name__} called use args: user_id\t{user_id}')
    with sqlite3.connect(NAME_DATABASE) as db:
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM clients WHERE user_id=:user_id""",
                       {'user_id': user_id})
        response = cursor.fetchall()
        logger.info(f'I get this information in sqlite: {response[0]}')
        return response[0]


def set_settings_in_db(user_id, key, value):
    logger.info(f'Function {set_settings_in_db.__name__} called with arguments: '
                f'\nuser_id {user_id}\tkey {key}\tvalue {value} ')

    with sqlite3.connect(NAME_DATABASE, check_same_thread=False) as db:
        cursor = db.cursor()
        request = ''
        if key == 'language':
            request = """UPDATE clients SET language = ? WHERE user_id = ?"""
        elif key == 'currency':
            request = """UPDATE clients SET currency = ? WHERE user_id = ?"""
        elif key == 'status':
            request = """UPDATE clients SET status = ? WHERE user_id = ?"""

        data = (value, user_id)
        cursor.execute(request, data)
        db.commit()


def create_history_record(user_id, hist_dict):
    logger.info(f'Function {create_history_record.__name__} called with arguments: '
                f'user_id {user_id}\thist_dict\n{hist_dict}')

    with sqlite3.connect(NAME_DATABASE) as db:
        cursor = db.cursor()
        request = """INSERT INTO requests VALUES (NULL,?,?,?,?,?,?,?,?) """
        cursor.execute(
            request,
            (
                user_id,
                hist_dict['command'],
                hist_dict['order'],
                hist_dict['city'],
                hist_dict['hotel_count'],
                hist_dict['photo_count'],
                hist_dict['date'],
                hist_dict['hotels']
            )
        )
        db.commit()


def get_history_from_db(user_id):
    logger.info(f'Function {get_history_from_db.__name__} called with argument: user_ id {user_id}')

    with sqlite3.connect(NAME_DATABASE) as db:
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM requests WHERE user_id=:user_id""",
                       {'user_id': user_id})
        response = cursor.fetchall()
        logger.info(f'Get response from db \n{response}')
        return response


#################################### секция redis ####################################


def check_user_in_redis(user_id):
    """
    проверка наличия присутствия пользователя.
    сначала проверяем в редисе, если в редисе нет, проверяем в sqlite. если в sqlite нет, то создаём пользователя
    и загружаем его в редис
    :param message:
    :return:
    """

    logger.info(f'Function {check_user_in_redis.__name__} called use args: user_id\t{user_id}')

    result_in_redis = redis_db.hgetall(user_id)

    if len(result_in_redis) == 0:
        logger.info(f"user wasn't found in redis")
        return False
    else:
        logger.info(f"user was found in redis")
        return True


def create_user_in_redis(user_id, language,first_name,last_name):
    """
    :param msg:
    :return:
    """
    logger.info(f'Function {create_user_in_redis.__name__} called with args: '
                f'user_id{user_id}, language {language}, first name {first_name}, last name {last_name}')

    if language not in language_dict.keys():
        language= 'en'
    if not check_user_in_db(user_id=user_id):
        create_user_in_db(user_id=user_id, language=language_dict[language])
    user_id, language, currency, status = get_user_from_bd(user_id=user_id)
    redis_db.hset(user_id, mapping={'language': language})
    redis_db.hset(user_id, mapping={'currency': currency})
    redis_db.hset(user_id, mapping={'status': status})
    redis_db.hset(user_id, mapping={'first_name': first_name})
    redis_db.hset(user_id, mapping={'last_name': last_name})
    logger.info(f'user with id {user_id} created ')


def set_settings(user_id, key, value):
    logger.info(f'Function {set_settings_in_db.__name__} called with arguments: '
                f'user_id {user_id}\tkey {key}\tvaluse {value}')

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
    elif key == 'command':
        redis_db.hset(user_id, mapping={'command': value})
    elif key == 'date1':
        redis_db.hset(user_id, mapping={'date1': value})
    elif key == 'date2':
        redis_db.hset(user_id, mapping={'date2': value})
    else:
        logger.warning(f'Command {key} with {value} not found')


def get_settings(user_id, key=False):
    logger.info(f'Function {get_settings.__name__} called with arguments: '
                f'user_id {user_id}\tkey {key}')
    if key in redis_db.hgetall(user_id).keys():
        logger.info(f'Function {get_settings.__name__} completed successfully')
        return redis_db.hget(user_id, key)
    else:
        logger.warning(f'Command key {key}')


def set_navigate(user_id, value):
    logger.info(f'Function {set_navigate.__name__} called with argument: '
                f'user_id {user_id}\tvalue{value}')

    redis_db.hset(user_id, mapping={'status': value})


def get_navigate(user_id):
    logger.info(f'Function {get_navigate.__name__} called with argument: '
                f'user_id {user_id}')
    result = redis_db.hget(user_id, 'status')
    logger.info(f'Redis return: {result}')
    return result
    # return re.search(r'\w+', str(result)[2:])[0]


def set_history(user_id, result):
    """
    {'command': 'low price', 'city': 'Выборг', 'hotel_count': '12', 'photo_count': '3', 'order': 'PRICE', 'date': 1639429200.0, 'hotels': 'ссылка1*ссылка2*ссылка*3'}
    :param user_id:
    :param result:
    :return:
    """
    logger.info(f'Function {set_history.__name__} called with argument: '
                f'user_id {user_id}\tresult:\n{result}')
    y, m, d = [int(i) for i in str(datetime.datetime.now().date()).split('-')]
    date = get_timestamp(y, m, d)
    result_from_redis = redis_db.hgetall(user_id)
    # подготовка данных к запихиванию в sql
    result_from_redis.update({'date': date})
    result_from_redis.update({'hotels': result})
    del result_from_redis['language']
    del result_from_redis['currency']
    del result_from_redis['status']

    create_history_record(user_id=user_id, hist_dict=result_from_redis)

    redis_db.delete(user_id)


def kill_user(user_id):
    logger.info(f'Function {kill_user.__name__} called with arg {user_id}')
    if check_user_in_redis(user_id):
        redis_db.delete(user_id)
        logger.info(f'hitman report: user with id {user_id} was killed')
