from decouple import config
import sqlite3
import telebot

API_TOKEN = config('TOKEN')
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(content_types=['text'])
def start_message(message):
    if message.text.lower() == '/start':
        bot.send_message(message.from_user.id, 'Your welcome')
    elif message.text == '/help':
        bot.send_message(message.from_user.id, "я ничего не умею")

bot.polling(none_stop=True)
