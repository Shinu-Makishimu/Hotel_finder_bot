import sqlite3
import functools

import telebot.types
from telebot import TeleBot
from settings import API_TOKEN, commands_list
from database import redis_db, check_user, create_user
from keyboard import settings_keyboard, main_menu_keyboard, language_keyboard, money_keyboard

bot = TeleBot(API_TOKEN)


# памятка по отслеживанию пользователя

# Шаблон для работы с пользователем:
# поймать ответ, фильтр тип ответа. ключ, начинается с...
# проверить пользователя на существование и/или проверить положение пользователя (status)
# занести в базу положение пользователя в меню
# показать пользователю что либо
#


@bot.message_handler(commands=['start'])
def start_message(message):
    """
    обработчик команды старт
    :param message:
    :return:
    """
    if not check_user(message):
        create_user(message)

    reply = '\npls enter comm'
    user_id = message.from_user.id
    status = redis_db.hget(user_id, 'status')

    if status is None:
        reply = '\npls add your settings first'
        kb = settings_keyboard
        bot.send_message(message.chat.id, 'settings', reply_markup=kb)
    elif status == 0:
        reply = 'welcome back'
    bot.send_message(message.chat.id, 'this is hello message' + reply)


@bot.message_handler(commands=['help'])
def help_message(message):
    if not check_user(message):
        create_user(message)

    user_id = message.from_user.id
    reply = 'this is comm_list'
    lang = redis_db.hget(user_id, 'language')

    for i_comm in commands_list:
        reply += '/' + i_comm + '\n'

    # TODO: добавить описание команд


@bot.message_handler(commands='settings')
def settings_menu(message):
    """
    Главное меню настроек
    :param call:
    :return:
    """
    if not check_user(message):
        create_user(message)
    user_id = message.from_user.id
    redis_db.hset(user_id, 'status', 1)

    bot.send_message(user_id, 'settings menu', reply_markup=settings_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startwith('set'))
def callback_settings(call):
    """
    Подменю настроек
    :param call:
    :return:
    """
    user_id = call.message.chat.id

    if call.data == 'set_country':
        bot.send_message(user_id, 'your country')
    elif call.data == 'set_money':
        bot.send_message(user_id, 'your answer ', reply_markup=money_keyboard)
    elif call.data == 'set_language':
        bot.send_message(user_id, 'your answer ', reply_markup=language_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startwith('money'))
def callback_money(call):
    """
    запись в бд параметра валюты
    :param call:
    :return:
    """
    user_id = call.message.chat.id
    if call.data.endswith('RUB'):
        redis_db.hset(user_id, 'money', 'RUB')
    elif call.data.endswith('USD'):
        redis_db.hset(user_id, 'money', 'USD')
    elif call.data.endswith('EUR'):
        redis_db.hset(user_id, 'money', 'EUR')
    bot.send_message(user_id, f'now, your money is {call.data[6:]}')
    # TODO: отправить пользвателя в главное меню.


@bot.callback_query_handler(func=lambda call: call.data.startwith('language'))
def callback_language(call):
    """
    запись в бд параметра языка
    :param call:
    :return:
    """
    user_id = call.message.chat.id

    if call.data.endswith('RUSS'):
        redis_db.hset(user_id, 'language', 'RUSS')
    elif call.data.endswith('ENGL'):
        redis_db.hset(user_id, 'language', 'ENGL')
    elif call.data.endswith('ESPA'):
        redis_db.hset(user_id, 'language', 'ESPA')

    bot.send_message(user_id, f'now, your money is {call.data[6:]}')
    # TODO: отправить пользвателя в главное меню.


@bot.message_handler(content_types=['text'])
def text_reply(message):
    """
    Тут обработчик текстовых ответов на вопросы о цене, радиусе поиска, городе
    :param message:
    :return:
    """
    user_id = message.from_user.id
    status = redis_db.hget(user_id, 'status')
    if status == 1:
        # TODO: найти способ проверить страну на корректность
        redis_db.hset(user_id, 'country', )


bot.infinity_polling()
