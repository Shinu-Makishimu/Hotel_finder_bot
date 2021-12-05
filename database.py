import sqlite3
import redis
from datetime import datetime


# структура базы данных:
# user_id id юзера
# user_name имя
# user_surname фамилмя
# username ник
# status на чем пользователь остановился
# request  его запросы

# user_data  должна содержать user_id, user_name, user_surname, username


def add_user_to_db(user_data):
    """
    это функция для работы с базой данных
    :param user_data:
    :return:
    """
    user_id, user_name, user_surname, username = user_data
    user_status = True
    user_history = ''
    connection = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM clients WHERE user_id = {user_id}".format(user_id=user_id))
    responce = cursor.fetchone()
    if responce is None:
        cursor.execute("INSERT INTO clients VALUES(?,?,?,?,?);", (
            user_id,
            user_name,
            user_surname,
            username,
            user_history)
                       )
        connection.commit()
        return 'пользователь создан'
    else:
        cursor.execute("SELECT * FROM clients WHERE user_id = {user_id}".format(user_id=user_id))
        responce = cursor.fetchone()
        return 'пользователь существует'


class User:
    """
    в классе пользователь будут хранится данные пользователя во время сессии.
    когда пользователь запускает диалог, запускается классметод get_user.
    Если пользователь есть в словаре
    """
    users = dict()

    # tusers = {1234: '244', 35341: 'dsfgsg', 251232: 'dsfs'}
    # redis = redis.Redis()

    def __init__(self, user_data):
        self.id = user_data[0]
        self.name = user_data[1]
        self.surname = user_data[2]
        self.user_req = []
        self.req_data = datetime.now()
        self.is_running = False
        # self.lang = 'eng'
        # self.step = dict()
        User.add_user(user_data[0], self)

    @classmethod
    def add_user(cls, id, user):
        cls.users[id] = user
        print(" сработал адд юзер из классметода")

    @classmethod
    def get_user(cls, user_data):
        id = user_data[0]
        if id in cls.users.keys():
            print('сработал гетюзер. пользователь найден')
            user_obj = cls.users[id]
        else:
            print('сработал гетюзер. не найден')
            user_data_from_db = test_get_user_from_db(id)  # запрос на наличие пользователя в бж
            print(user_data_from_db)
            if not user_data_from_db:  # если вернулся None
                test_add_new_user_to_db(user_data)  # добавляем в базу
            user_obj = User(user_data_from_db)  # иначе обновляем запись о пользователе
        print(user_obj)
        return user_obj


def work_with_keys(user_data, key):
    client = User.get_user(user_data)
    client.user_req.append(key)


def return_all_req(user_data):
    client = User.get_user(user_data)
    return client.user_req


def test_get_user_from_db(user_id):
    """
    это функция для работы с базой данных
    :param user_data:
    :return:
    """
    connection = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM clients WHERE user_id = {user_id}".format(user_id=user_id))
    responce = cursor.fetchone()
    print('сработал гетюзер из дб его ответ:', responce)
    if responce is None:
        return False
    else:
        cursor.execute("SELECT * FROM clients WHERE user_id = {user_id}".format(user_id=user_id))
        responce = cursor.fetchone()
        print('юзер нашёлся в дб.его ответ:', responce)
        return responce


def test_add_new_user_to_db(user_data):
    """
    это функция для работы с базой данных
    :param user_data:
    :return:
    """
    user_id, user_name, user_surname, username = user_data
    user_history = ''
    connection = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM clients WHERE user_id = {user_id}".format(user_id=user_id))
    responce = cursor.fetchone()
    if responce is None:
        cursor.execute("INSERT INTO clients VALUES(?,?,?,?,?);", (
            user_id,
            user_name,
            user_surname,
            username,
            user_history)
                       )
        connection.commit()
        return True
    else:
        raise Exception('ПОЛЬЗОВАТЕЛЬ УЖЕ ЕСТЬ!!')





























# d = {1234: '244', 35341: 'dsfgsg', 251232: 'dsfs'}
# a = 1234
# b = a in d.keys()
# print(b)
# if a in d.keys():
#     print('da')
# else:
#     print('net')


# tuser_data = [1234, 'asdg','adgasd','adgasd']
# a = User.get_user(tuser_data)
# print(a)
######################################################################################
    #
    #
    # @classmethod
    # def test_get_user(cls, user_data):
    #     id = user_data[0] # кладем id в переменную
    #     test_user_obj = cls.redis.get(id) #запрос в редис на наличие присутствие записи о польлзователе
    #     if cls.redis.get(id) is None: #если нет в редисе
    #         user_data_from_db = test_get_user_from_db(id) # запрос на наличие пользователя в бж
    #         if not user_data_from_db:# если вернулся None
    #             test_add_new_user_to_db(user_data) #добавляем в базу
    #         test_user_obj = User(user_data_from_db)# иначе обновляем запись о пользователе
    #     return test_user_obj #возвращаем объект



# class User:
#     """
#     вместо базы данных пока что буду пользоваться классом. Ровно до того момента как будут реализованы функции.
#     в дальнейшем переделать под sql
#     """
#     users = dict()
#
#     def __init__(self, user_id, first_name, last_name):
#         self.id = user_id
#         self.name = first_name
#         self.surname = last_name
#         self.user_req = []
#         self.is_running = False
#         User.add_user(user_id, self)
#
#     @classmethod
#     def add_user(cls, id, user):
#         cls.users[id] = user
#
#     @classmethod
#     def get_user(cls, id, name, surname):
#         if not id in cls.users.keys():
#             user_object = User(id, name, surname)
#         user_object = cls.users[id]
#
#         return user_object

#
#
# #####################################################################################
# class User:
#
#     def connect_to_db(self):
#         self.connect = sqlite3.connect('bot.db')
#         self.cursor = self.connect.cursor()
#
#
#     def close_connect(self):
#         self.connect.close()
#
#
#     def get_all_id(self):
#         self.connect_to_db()
#         request = 'SELECT user_id FROM clients'
#         result = self.cursor.execute(request).fetchall()
#         self.close_connect()
#
#         return [i[0] for i in result] #вернет лист результатов
#
#     def get_field(self, user_id, field):
#         self.connect_to_db()
#         request = "SELECT {field} FROM clients WHERE user_id=?".format(field=field)
#         result = self.cursor.execute(request, (user_id,)).fetchone()
#         self.close_connect()
#         return result[0]
#
#     def set_field(self, user_id, field, value):
#         self.connect_to_db()
#         request = "UPDATE clients SET {field}=? WHERE user_id=?".format(field=field)
#         self.cursor.execute(request, (value, user_id))
#         self.connect.commit()
#         self.close_connect()


# @classmethod
#     def get_user(cls, user_data):
#         id = user_data[0]
#         if id in cls.users.keys():
#             print('пользователь найден')
#             user_obj = cls.users[id]
#         else:
#             print('не найден')
#             user_obj = User(user_data)
#
#         return user_obj
