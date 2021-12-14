from decouple import config

buttons_eng = {'low': 'Low price',
               'high': 'High price',
               'best': 'Best price',
               'hist': 'Your history',
               'main_h': 'Click on the button with the desired operation',
               'greet': 'This is a low-quality bot from a dumb developer.\n(btw, your id is ',
               'help': 'Following commands are avaliable: \n'}  # словарь в который будут положены названия кнопок на английском
buttons_rus = dict()  # словарь в который будут положены названия кнопок на русском

content_type_ANY = ['audio', 'document', 'photo', 'sticker', 'video', 'voice', 'contact', 'caption']

commands_list = ['start','lowprice', 'highprice', 'bestdeal', 'settings']

API_TOKEN = config('KEY')

H_API_TOKEN = config('APIKEY')
HOST = 'hotels4.p.rapidapi.com'
url = "https://hotels4.p.rapidapi.com/locations/v2/search"

NAME_DATABASE = 'bot_v2.db'
excluded_types = ['audio', 'document', 'photo', 'sticker', 'video', 'voice']  # список непринимаемых типов данных.

