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


def add_user(user_data):
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
    cursor.execute("SELECT user_id FROM clients WHERE user_id = {user_id}". format(user_id=user_id))
    responce = cursor.fetchone()
    print(responce)
    if responce is None:
        cursor.execute("INSERT INTO clients VALUES(?,?,?,?,?,?);", (
            user_id,
            user_name,
            user_surname,
            username,
            user_status,
            user_history)
                       )
        connection.commit()
        return 'пользователь создан'
    else:
        cursor.execute("SELECT * FROM clients WHERE user_id = {user_id}".format(user_id=user_id))
        responce = cursor.fetchone()
        print(responce)
        return 'пользователь существует'





# redis = redis.Redis()
# redis.mset({'croatia': 'zagreb', 'russia': 'vyborg', 'germany': 'berlin'})
# print(redis.get('russia'))
# print(redis.get('france'))





class User:
    """
    в классе пользователь будут хранится данные пользователя во время сессии
    """
    # users = dict()
    redis = redis.Redis()

    def __init__(self, user_data):
        self.id = user_data[0]
        self.name = user_data[1]
        self.surname = user_data[2]
        self.user_req = []
        self.req_data = datetime.now()
        self.is_running = False
        User.add_user(user_data[0], self)

    @classmethod
    def add_user(cls, id, user):
        cls.redis.mset({str(id): user})


    @classmethod
    def get_user(cls, user_data):
        if cls.redis.get(user_data[0]) is None:
            User(user_data)
        return cls.redis.get(user_data[0])





######################################################################################
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