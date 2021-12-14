from decouple import config
import redis

content_type_ANY = ['audio', 'document', 'photo', 'sticker', 'video', 'voice', 'contact', 'caption']

commands_list = ['start','lowprice', 'highprice', 'bestdeal', 'settings']

API_TOKEN = config('KEY')

H_API_TOKEN = config('APIKEY')
HOST = 'hotels4.p.rapidapi.com'
url = "https://hotels4.p.rapidapi.com/locations/v2/search"

NAME_DATABASE = 'bot.db'

redis_db = redis.StrictRedis(host='localhost', port=6379, db=1, charset='utf-8', decode_responses=True)

excluded_types = ['audio', 'document', 'photo', 'sticker', 'video', 'voice']  # список непринимаемых типов данных.

