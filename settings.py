from decouple import config

buttons_eng = {'low': 'Low price',
               'high': 'High price',
               'best': 'Best price',
               'hist': 'Your history',
               'main_h': 'Click on the button with the desired operation',
               'greet': 'This is a low-quality bot from a dumb developer.\n(btw, your id is ',
               'help': 'Following commands are avaliable: \n'} # словарь в который будут положены названия кнопок на английском
buttons_rus = dict() # словарь в который будут положены названия кнопок на русском

API_TOKEN = config('KEY')
commands = {'start': 'Start using this bot',
            'main': '4 butttons',
            'lowprice': 'find low',
            'bestdeal': 'find best',
            'highprice': 'find high',
            'history': "Show user's history" }

excluded_types = ['audio', 'document', 'photo','sticker', 'video', 'voice'] # список непринимаемых типов данных.

class User:
    """
    вместо базы данных пока что буду пользоваться классом. Ровно до того момента как будут реализованы функции.
    в дальнейшем переделать под sql
    """
    users = dict()

    def __init__(self, chat_id, first_name, last_name):
        self.id = chat_id
        self.name = first_name
        self.surname = last_name
        User.add_user(chat_id, self)

    @classmethod
    def add_user(cls, id, user):
        cls.users[id] = user

    @classmethod
    def get_user(cls, id,name,surname):
        if not id in cls.users.keys():
            object = User(id,name,surname)
        object=cls.users[id]

        return object