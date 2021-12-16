import sqlite3
import functools
import telebot.types
from loguru import logger
from telebot import TeleBot
from settings import API_TOKEN, NAME_DATABASE, logger_config
from accessory import get_timestamp, get_date
from database import check_user_in_redis,create_user_in_redis, set_settings, get_settings, set_navigate, get_navigate,\
    create_bd_if_not_exist, set_history,get_history_from_db, kill_user
from keyboard import settings_keyboard, main_menu_keyboard, language_keyboard, money_keyboard, photo_keyboard
from language import interface
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from os import path
from bot_requests.botreqvests import make_locations_list

bot = TeleBot(API_TOKEN)
logger.configure(**logger_config)
logger.info("\\"*50+'new session started'+ "//"*50)
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
    kill_user(message)

    if not check_user_in_redis(msg=message):
        create_user_in_redis(msg=message)
    logger.info("\n" + "=" * 100 + "\n")
    logger.info(f'"start" command is called')
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

# отлов команды настройки
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
    logger.info(f'"settings" command is called')
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

    user_id = call.from_user.id
    logger.info(f'Function {main_handler.__name__} called and use arg: user_id{user_id}')
    # TODO: УБРАТЬ ДУБЛИРОВАНИЕ КОДА!!!!!!!!!!!!!!!!!!!!!!!

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
    logger.info(f'Function {starting_commands.__name__} called and use argument: {message.text}')
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
    logger.info(f'Function {callback_settings.__name__} called and use argument: '
                f'user_id {user_id} and call.data {call.data}')


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
    user_id = call.from_user.id
    logger.info(f'Function {callback_money.__name__} called and use argument: '
                f'user_id {user_id} and call data {call.data}')
    bot.answer_callback_query(call.id)

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
    logger.info(f'Function {callback_language.__name__} called and use argument: '
                f'user_id {user_id} and call data {call.data}')

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
    logger.info(f'Function {photo_handler.__name__} called and use argument: '
                f'user_id {user_id} and call data {call.data}')
    if call.data.endswith('yes'):
        bot.send_message(user_id, interface['questions']['photo'][language])
    else:
        set_settings(msg=call, key='photo_count', value=0)
        set_navigate(msg=call, value='date')
        choose_date_1(call)


def make_dialogue(message):

    user_id = message.from_user.id
    logger.info(f'Function {make_dialogue.__name__} called and use argument: '
                f'user_id {user_id}')

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
    logger.info(f'Function {text_reply.__name__} called and use argument user_id : {user_id}')

    if status == 'date':
        choose_date_1(message)
    elif status == "city_h":
        if message.text.strip().replace(' ', '').replace('-', '').isalpha():
            get_locations(message)
        else:
            bot.send_message(user_id, interface['errors']['city'][language])
        make_dialogue(message)
    elif status == 'count_h':
        if ' ' not in message.text.strip() and message.text.strip().isdigit() and 0 < int(message.text.strip()) <= 20:
            set_settings(msg=message, key='hotel_count', value=message.text.strip())
            set_navigate(msg=message, value='count_p')
            bot.send_message(user_id, interface['responses']['ok'][language])
        else:
            bot.send_message(user_id, interface['errors']['count'][language])
        make_dialogue(message)
    elif status == 'count_p':
        if ' ' not in message.text.strip() and message.text.strip().isdigit() and 0 < int(message.text.strip()) <= 5:
            set_settings(msg=message, key='photo_count', value=message.text.strip())
            bot.send_message(user_id, interface['responses']['ok'][language])
            set_navigate(msg=message, value='date')
            choose_date_1(message)

        else:
            bot.send_message(user_id, interface['errors']['count'][language])
            make_dialogue(message)



def choose_date_1(message):
    logger.info(f'Function {choose_date_1.__name__} called')

    language = get_settings(msg=message, key='language')
    reply = interface['questions']['date1'][language]
    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale=language).build()
    bot.send_message(message.chat.id, f"{reply} {LSTEP[step]}", reply_markup=calendar)


def choose_date_2(message):
    logger.info(f'Function {choose_date_2.__name__} called')

    language = get_settings(msg=message, key='language')
    reply = interface['questions']['date2'][language]
    calendar, step = DetailedTelegramCalendar(calendar_id=2, locale=language).build()
    bot.send_message(message.chat.id, f"{reply} {LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def callback_calendar(call):
    logger.info(f'Function {callback_calendar.__name__} called ')

    result, key, step = DetailedTelegramCalendar(calendar_id=1).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Calendar 1: Select {LSTEP[step]}", call.message.chat.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"You selected {result} in calendar 1", call.message.chat.id,call.message.message_id)
        y, m, d = [int(i) for i in str(result).split('-')]
        result = get_timestamp(y, m, d)
        set_settings(msg=call, key='date1', value=result)
        choose_date_2(call.message)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def callback_calendar(call):
    logger.info(f'Function {callback_calendar.__name__} called')

    result, key, step = DetailedTelegramCalendar(calendar_id=2).process(call.data)

    if not result and key:
        bot.edit_message_text(f"Calendar 2: Select {LSTEP[step]}", call.message.chat.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        first_date = get_settings(msg=call, key='date1')
        y, m, d = [int(i) for i in str(result).split('-')]
        second_date = get_timestamp(y, m, d)

        if float(first_date) >= float(second_date):
            bot.send_message(call.message.chat.id, 'неправильная дата')
            set_settings(msg=call, key='date1', value=' ')
            choose_date_1(call.message)
        else:
            bot.edit_message_text(f"You selected {result} in calendar 2", call.message.chat.id,call.message.message_id)
            set_settings(msg=call, key='date2', value=second_date)
            # set_navigate()
            hotel_result(call)



def get_locations(message):

    user_id = message.from_user.id
    language = get_settings(msg=message, key='language')
    locations = make_locations_list(message)
    logger.info(f'Function {get_locations.__name__} called and use argument user_id : {user_id}')

    if not locations or len(locations) < 1:
        bot.send_message(user_id, interface['errors']['count'][language])
    elif locations.get('bad_request'):
        bot.send_message(user_id, interface['errors']['bad_request'][language])
    else:
        menu = telebot.types.InlineKeyboardMarkup()
        for loc_name, loc_id in locations.items():
            menu.add(telebot.types.InlineKeyboardButton(
                    text=loc_name,
                    callback_data='code' + loc_id)
                )
        bot.send_message(user_id, interface['questions']['loc_choose'][language], reply_markup=menu)
        #тут надо отловить нажатие кнопки в списке локаций


@bot.callback_query_handler(func=lambda call: True)
def hotel_handler(call):
    logger.info(f'Function {hotel_handler.__name__} called ')

    language = get_settings(msg=call, key='language')
    set_settings(msg=call, key='city', value=call.data)
    status = get_navigate(msg=call)
    bot.answer_callback_query(call.id)
    bot.edit_message_text(interface['responses']['ok'][language], call.message.chat.id, call.message.message_id)
    set_navigate(msg=call, value='count_h')
    make_dialogue(call)


def hotel_result(message):

    user_id = message.from_user.id
    logger.info(f'Function {hotel_result.__name__} called and use argument user_id : {user_id}')

    # тут происходит магия поиска и возврата отелей
    result = 'ссылка1*ссылка2*ссылка*3'
    # тут происходит магия показа отелей
    set_navigate(msg=message, value='main')
    print(get_settings(msg=message))
    set_history(user_id, result)
    bot.send_message(user_id, 'дно достигнуто')


def get_history(call):
    user_id = call.from_user.id
    ans = get_history_from_db(user_id)
    for i_element in ans:
        pass
    bot.send_message(user_id, ans)


bot.infinity_polling()
