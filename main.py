import sqlite3
import functools

import telebot.types
from telebot import TeleBot
from settings import API_TOKEN, commands_list
from database import check_user, create_user, set_navigate, set_settings, get_navigate, get_settings
from keyboard import settings_keyboard, main_menu_keyboard, language_keyboard, money_keyboard
from language import interface

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
    new = False
    if not check_user(message=message):
        create_user(message=message)
        new = True

    user_id = message.from_user.id
    person = f' {message.from_user.first_name} {message.from_user.last_name}!\n'
    country, currency, language = get_settings(message)
    reply = interface['responses']['greeting_1'][language] + person

    if new:
        reply += interface['responses']['greeting_new'][language]
    else:
        reply += interface['responses']['greeting_old'][language]

    bot.send_message(user_id, reply, reply_markup=main_menu_keyboard)


@bot.message_handler(commands=['help'])
def help_message(message):
    if not check_user(message=message):
        create_user(message=message)

    user_id = message.from_user.id

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
    # TODO: отлов кнопки сеттингс?
    if not check_user(message=message):
        create_user(message=message)

    country, currency, language = get_settings(message)
    user_id = message.from_user.id
    set_navigate(message=message, value='sett')
    reply = "{menu}\n{ans}\n {your_lang} {lang}\n {your_cur} {cur}".format(
        menu=interface['elements']['settings_menu'][language],
        ans=interface['responses']['your_settings'][language],
        your_lang=interface['responses']['current_language'][language],
        lang=language,
        your_cur=interface['responses']['current_currency'][language],
        cur=currency
    )

    bot.send_message(user_id, reply, reply_markup=settings_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('main'))
def main_handler(call):
    """
    ловля кнопки сеттингс
    :param call:
    :return:
    """
    # TODO: УБРАТЬ ДУБЛИРОВАНИЕ КОДА!!!!!!!!!!!!!!!!!!!!!!!
    user_id = call.from_user.id
    if call.data.endswith('settings'):
        settings_menu(call)
    elif call.data.endswith('low'):
        set_navigate(message=call, value='lowprice')
        set_settings(user_id=user_id, key='order', value='PRICE')
    elif call.data.endswith('high'):
        set_navigate(message=call, value='highprice')
        set_settings(user_id=user_id, key='order', value='PRICE_HIGHEST_FIRST')
    elif call.data.endswith("best"):
        set_navigate(message=call, value='bestdeal')
        set_settings(user_id=user_id, key='order', value='DISTANCE_FROM_LANDMARK')
    bot.send_message(user_id, 'есть пробитие')


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def starting_commands(message):
    """
    отлов нажатия основных рабочих кнопочек
    :param message:
    :return:
    """
    # TODO: УБРАТЬ ДУБЛИРОВАНИЕ КОДА!!!!!!!!!!!!!!!!!!!!!!!
    user_id = message.from_user.id
    status = get_navigate(message)


    if status == 'new':
        reply = responses['responses']['default_sett'][language]
        bot.send_message(user_id, reply)

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


    bot.send_message(user_id, 'есть пробитие')


@bot.callback_query_handler(func=lambda call: call.data.startswith('set'))
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
        start_message(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('money'))
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
    else:
        settings_menu(call)
    set_navigate(message=call, value='main')
    settings_menu(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('language'))
def callback_language(call):
    """
    запись в бд параметра языка
    :param call:
    :return:
    """
    user_id = call.message.chat.id
    lang = ''

    if call.data.endswith('RUSS'):
        lang = 'ru'
        set_settings(user_id, 'language', 'ru')
    elif call.data.endswith('ENGL'):
        lang = 'en'
        set_settings(user_id, 'language', 'en')
    elif call.data.endswith('ESPA'):
        lang = 'es'
        set_settings(user_id, 'language', 'es')
    else:
        settings_menu(call)

    reply = interface['responses']['saved'][lang]
    bot.send_message(user_id, reply)
    settings_menu(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel'))
def callback_cancel(call):
    user_id = call.message.chat.id
    # loc =  get_navigate()


def make_dialogue():
    order, currency, language = get_settings(message)
    reply = interface['questions']['city'][language]



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





bot.infinity_polling()
