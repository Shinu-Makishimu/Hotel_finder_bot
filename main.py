import sqlite3
import functools
import telebot.types
from telebot import TeleBot
from settings import API_TOKEN, NAME_DATABASE, commands_list
from database import check_user_in_redis,create_user_in_redis, set_settings, get_settings, set_navigate, get_navigate,\
    create_bd_if_not_exist, set_history,get_history_from_db
from keyboard import settings_keyboard, main_menu_keyboard, language_keyboard, money_keyboard, photo_keyboard
from language import interface

from os import path

bot = TeleBot(API_TOKEN)

if not path.isfile(NAME_DATABASE):
    create_bd_if_not_exist()


# памятка по отслеживанию пользователя

# Шаблон для работы с пользователем:
# поймать ответ, фильтр тип ответа. ключ, начинается с...
# проверить пользователя на существование и/или проверить положение пользователя (status)
# занести в базу положение пользователя в меню
# показать пользователю что либо
#
# call.message.chat.id # id чата
#      from_user.id # id юзера


@bot.message_handler(commands=['start'])
def start_message(message):
    """
    обработчик команды старт
    :param message:
    :return:
    """

    if not check_user_in_redis(msg=message):
        create_user_in_redis(msg=message)

    user_id = message.from_user.id
    person = f' {message.from_user.first_name} {message.from_user.last_name}!\n'
    status = get_navigate(msg=message)
    language = get_settings(msg=message, key='language')

    reply = interface['responses']['greeting_1'][language] + person

    if status == 'new':
        reply += interface['responses']['greeting_new'][language]
    else:
        set_navigate(msg=message, value='main')
        reply += interface['responses']['greeting_old'][language]

    bot.send_message(user_id, reply, reply_markup=main_menu_keyboard)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.from_user.id, 'хелп заглушка')

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
    check_user_in_redis(msg=message)

    currency = get_settings(msg=message, key='currency')
    language = get_settings(msg=message, key='language')
    user_id = message.from_user.id
    set_navigate(msg=message, value='sett')

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
    bot.answer_callback_query(call.id)
    if call.data.endswith('settings'):
        settings_menu(call)
    elif call.data.endswith('hist'):
        set_settings(msg=call, key='command', value='history')
        get_history(call)
    elif call.data.endswith('low'):
        set_settings(msg=call, key='command', value='low price')
        set_settings(msg=call, key='order', value='PRICE')
        set_navigate(msg=call, value='city_h')
        make_dialogue(call)
    elif call.data.endswith('high'):
        set_settings(msg=call, key='command', value='high price')
        set_settings(msg=call, key='order', value='PRICE_HIGHEST_FIRST')
        set_navigate(msg=call, value='city_h')
        make_dialogue(call)
    elif call.data.endswith("best"):
        set_settings(msg=call, key='command', value='best deal')
        set_settings(msg=call, key='order', value='DISTANCE_FROM_LANDMARK')
        set_navigate(msg=call, value='city_h')
        make_dialogue(call)



@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def starting_commands(message):
    """
    отлов нажатия основных рабочих кнопочек
    :param message:
    :return:
    """
    # TODO: УБРАТЬ ДУБЛИРОВАНИЕ КОДА!!!!!!!!!!!!!!!!!!!!!!!

    set_navigate(msg=message, value='main')
    if 'lowprice' in message.text:
        set_settings(msg=message, key='command', value='low price')
        set_settings(msg=message, key='order', value='PRICE')
        set_navigate(msg=message, value='city_h')
        make_dialogue(message)
    elif 'highprice' in message.text:
        set_settings(msg=message, key='command', value='high price')
        set_settings(msg=message, key='order', value='PRICE_HIGHEST_FIRST')
        set_navigate(msg=message, value='city_h')
        make_dialogue(message)
    else:
        set_settings(msg=message, key='command', value='best deal')
        set_settings(msg=message, key='order', value='DISTANCE_FROM_LANDMARK')
        set_navigate(msg=message, value='city_h')
        make_dialogue(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('set'))
def callback_settings(call):
    """
    Подменю настроек
    :param call:
    :return:
    """
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)

    # if call.data == 'set_country':
    #     bot.send_message(user_id, 'your country')
    if call.data == 'set_money':
        bot.send_message(user_id, 'your answer ', reply_markup=money_keyboard)
    elif call.data == 'set_language':
        bot.send_message(user_id, 'your answer ', reply_markup=language_keyboard)
    elif call.data == 'set_back':
        set_navigate(msg=call, value='main')
        start_message(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('money'))
def callback_money(call):
    """
    запись в бд параметра валюты
    :param call:
    :return:
    """
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    if call.data.endswith('RUB'):
        set_settings(msg=call, key='currency', value='RUB')
    elif call.data.endswith('USD'):
        set_settings(msg=call, key='currency', value='USD')
    elif call.data.endswith('EUR'):
        set_settings(msg=call, key='currency', value='EUR')
    else:
        settings_menu(call)
    settings_menu(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('language'))
def callback_language(call):
    """
    запись в бд параметра языка
    :param call:
    :return:
    """
    user_id = call.from_user.id
    lang = ''
    bot.answer_callback_query(call.id)

    if call.data.endswith('RUSS'):
        lang = 'ru'
        set_settings(msg=call, key='language', value='ru')
    elif call.data.endswith('ENGL'):
        lang = 'en'
        set_settings(msg=call, key='language', value='en')
    elif call.data.endswith('ESPA'):
        lang = 'es'
        set_settings(msg=call, key='language', value='es')
    else:
        settings_menu(call)

    reply = interface['responses']['saved'][lang]
    bot.send_message(user_id, reply)
    settings_menu(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel'))
def callback_cancel(call):
    user_id = call.message.chat.id
    # loc =  get_navigate()


@bot.callback_query_handler(func=lambda call: call.data.startswith('photo'))
def photo_handler(call):
    bot.answer_callback_query(call.id)

    user_id = call.from_user.id
    language = get_settings(msg=call, key='language')

    if call.data.endswith('yes'):
        bot.send_message(user_id, interface['questions']['photo'][language])
    else:
        set_settings(msg=call, key='photo_count', value=0)
        hotel_result(call)


def make_dialogue(message):
    # register_next_step изучить

    user_id = message.from_user.id

    language = get_settings(msg=message, key='language')
    order = get_settings(msg=message, key='order')
    status = get_navigate(msg=message)
    reply = interface['errors']['input'][language]

    if status == 'city_h':
        reply = interface['questions']['city'][language]
        bot.send_message(user_id, reply)
    elif status == 'count_h':
        reply = interface['questions']['count'][language] + '20'
        bot.send_message(user_id, reply)
    elif status == 'count_p':
        reply = interface['questions']['need_photo'][language]
        bot.send_message(user_id, reply, reply_markup=photo_keyboard)


@bot.message_handler(content_types=['text'])
def text_reply(message):
    """
    Тут обработчик текстовых ответов на вопросы о цене, радиусе поиска, городе
    :param message:
    :return:
    """
    user_id = message.from_user.id
    language = get_settings(msg=message, key='language')
    status = get_navigate(msg=message)
    from_user_text = message.text.strip()

    if status == "city_h":
        if from_user_text.replace(' ', '').replace('-', '').isalpha():
            set_settings(msg=message, key='city', value=from_user_text)
            set_navigate(msg=message, value='count_h')
            bot.send_message(user_id, interface['responses']['ok'][language])
        else:
            bot.send_message(user_id, interface['errors']['city'][language])
        make_dialogue(message)
    elif status == 'count_h':
        if ' ' not in from_user_text and from_user_text.isdigit() and 0 < int(from_user_text) <= 20:
            set_settings(msg=message, key='hotel_count', value=from_user_text)
            set_navigate(msg=message, value='count_p')
            bot.send_message(user_id, interface['responses']['ok'][language])
        else:
            bot.send_message(user_id, interface['errors']['count'][language])
        make_dialogue(message)
    elif status == 'count_p':
        if ' ' not in from_user_text and from_user_text.isdigit() and 0 < int(from_user_text) <= 5:
            set_settings(msg=message, key='photo_count', value=from_user_text)
            bot.send_message(user_id, interface['responses']['ok'][language])
            order = get_settings(msg=message, key='order')
            if order == 'DISTANCE_FROM_LANDMARK':
                best_deal_dialogue(message)
            hotel_result(message)

        else:
            bot.send_message(user_id, interface['errors']['count'][language])
            make_dialogue(message)


def hotel_result(message):
    user_id = message.from_user.id
    # тут происходит магия поиска и возврата отелей
    result = 'ссылка1*ссылка2*ссылка*3'
    # тут происходит магия показа отелей
    set_navigate(msg=message, value='main')
    set_history(user_id, result)
    bot.send_message(user_id, 'дно достигнуто')

def choose_date():
    pass



def best_deal_dialogue(message):
    #     2. Диапазон цен.
    # 3. Диапазон расстояния, на котором находится отель от центр
    pass


def get_history(call):
    user_id = call.from_user.id
    ans = get_history_from_db(user_id)
    for i_element in ans:
        pass
    bot.send_message(user_id, ans)


bot.infinity_polling()
