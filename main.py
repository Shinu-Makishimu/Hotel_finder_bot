import sqlite3
import functools

import telebot.types
from telebot import TeleBot
from settings import API_TOKEN, commands_list
from database import check_user, create_user, set_navigate, set_settings, get_navigate, get_settings
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
    user_id = message.from_user.id
    name = message.from_user.first_name
    surname = message.from_user.last_name

    if not check_user(message=message):
        create_user(message=message)

    reply = f'приветствие {name} {surname}'

    # country, currency, language = get_settings(message)
    bot.send_message(user_id, reply, reply_markup=main_menu_keyboard)

    # reply = '\npls enter comm'
    # user_id = message.from_user.id
    # status = get_navigate(message)
    #
    # if status == '':
    #     reply = '\npls add your settings first'
    #     kb = settings_keyboard
    #     bot.send_message(user_id, 'settings', reply_markup=kb)
    # elif status == 0:
    #     reply = 'welcome back'
    # bot.send_message(user_id, 'this is hello message' + reply)


@bot.message_handler(commands=['help'])
def help_message(message):
    if not check_user(message=message):
        create_user(message=message)

    user_id = message.from_user.id
    reply = 'this is comm_list'

    for i_comm in commands_list:
        reply += '/' + i_comm + '\n'
    bot.send_message(user_id, 'this is command menu')

    # TODO: добавить описание команд


@bot.message_handler(commands='settings')
def settings_menu(message):
    """
    Главное меню настроек
    :param message:
    :param call:
    :return:
    """
    if not check_user(message=message):
        create_user(message=message)
    user_id = message.from_user.id
    set_navigate(message=message, value='sett')
    bot.send_message(user_id, 'settings menu', reply_markup=settings_keyboard)



@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def starting_commands(message):
    if not check_user(message=message):
        create_user(message=message)
    user_id = message.chat.id
    set_navigate(message=message, value='main')
    if 'lowprice' in message.text:
        set_navigate(message=message, value='lowprice')
        set_settings(user_id=user_id, key='order', value='PRICE')
    elif 'highprice' in message.text:
        set_navigate(message=message, value='highprice')
        set_settings(user_id=user_id, key='order', value='PRICE_HIGHEST_FIRST')
    else:
        set_navigate(message=message, value='bestdeal')
        set_settings(user_id=user_id, key='order', value='DISTANCE_FROM_LANDMARK')

    bot.send_message(user_id, 'тут чето спросить')


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
    elif call.data == 'set_back':
        start_message()



@bot.callback_query_handler(func=lambda call: call.data.startwith('money'))
def callback_money(call):
    """
    запись в бд параметра валюты
    :param call:
    :return:
    """
    user_id = call.message.chat.id
    if call.data.endswith('RUB'):
        set_settings(user_id, 'money', 'RUB')
    elif call.data.endswith('USD'):
        set_settings(user_id, 'money', 'USD')
    elif call.data.endswith('EUR'):
        set_settings(user_id, 'money', 'EUR')
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
        set_settings(user_id, 'language', 'RUSS')
    elif call.data.endswith('ENGL'):
        set_settings(user_id, 'language', 'ENGL')
    elif call.data.endswith('ESPA'):
        set_settings(user_id, 'language', 'ESPA')

    bot.send_message(user_id, f'now, your money is {call.data[6:]}')
    # TODO: отправить пользвателя в главное меню.


@bot.callback_query_handler(func=lambda call: call.data.startwith('cancel'))
def callback_cancel(call):
    user_id = call.message.chat.id
    # loc =  get_navigate()


@bot.message_handler(content_types=['text'])
def text_reply(message):
    """
    Тут обработчик текстовых ответов на вопросы о цене, радиусе поиска, городе
    :param message:
    :return:
    """
    user_id = message.from_user.id
    status = get_navigate(message)
    if status == 1:
        pass
    # TODO: найти способ проверить страну на корректность

def get_search_parameters(message) -> None:
    """
    fixes search parameters
    :param msg: Message
    :return: None
    """

    user_id = message.chat.id
    status = get_navigate(message=message)



bot.infinity_polling()
