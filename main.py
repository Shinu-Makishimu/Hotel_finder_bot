import sqlite3
import functools
import telebot.types
from loguru import logger
from telebot import TeleBot
from settings import API_TOKEN, NAME_DATABASE, logger_config, commands_list

from accessory import get_timestamp, get_date
from database import check_user_in_redis,create_user_in_redis, set_settings, get_settings, set_navigate, get_navigate,\
    create_bd_if_not_exist, set_history,get_history_from_db, kill_user
from keyboard import settings_keyboard, main_menu_keyboard, language_keyboard, money_keyboard, photo_keyboard
from language import interface
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from os import path
from bot_requests.botreqvests import make_locations_list
from bot_requests.menu import start_reply, settings_reply

bot = TeleBot(API_TOKEN)
logger.configure(**logger_config)
logger.info("\n" +"\\"*50+'new session started'+ "//"*50+ "\n")

if not path.isfile(NAME_DATABASE):
    create_bd_if_not_exist()


# памятка по отслеживанию пользователя

# Шаблон для работы с пользователем:
# поймать ответ, фильтр тип ответа. ключ, начинается с...
# проверить пользователя на существование и/или проверить положение пользователя (status)
# занести в базу положение пользователя в меню
# показать пользователю что либо
# chat_id = message.chat.id
# chat_id = call.message.chat.id # id чата
# user_id = call.from_user.id
# user_id = message.from_user.id # id юзера
# TODO: сделать обработчик "левой" команды


@bot.message_handler(commands=['start', 'lowprice', 'highprice', 'bestdeal','settings','help'])
def commands_catcher(message):
    """
    отлов команд
    :param message:
    :return:
    """
    logger.info(f'Function {commands_catcher.__name__} called '
                f'and use argument: {message.text}')
    if message.text == commands_list[0]:
        kill_user(message.from_user.id)
        create_user_in_redis(
            user_id=message.from_user.id,
            language=message.from_user.language_code,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        logger.info(f'"start" command is called')
    main_menu(user_id=message.from_user.id, command=message.text.strip('/'), chat_id=message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('main'))
def buttons_catcher_main(call):
    logger.info(f'Function {buttons_catcher_main.__name__} called and use arg: '
                f'user_id{call.from_user.id} and data: {call.data}')
    main_menu(user_id=call.from_user.id, command=call.data.split('_')[1], chat_id=call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('set'))
def buttons_catcher_settings(call):
    logger.info(f'Function {buttons_catcher_settings.__name__} called and use arg: '
                f'user_id{call.from_user.id} and data: {call.data}')
    logger.info(f'Function settings menu called')
    bot.answer_callback_query(call.id)

    if call.data == 'set_money':
        bot.send_message(call.message.chat.id, 'your answer ', reply_markup=money_keyboard)
    elif call.data == 'set_language':
        bot.send_message(call.message.chat.id, 'your answer ', reply_markup=language_keyboard)
    elif call.data == 'set_back':
        set_navigate(user_id=call.from_user.id, value='main')
        main_menu(user_id=call.from_user.id, command='start', chat_id=call.message.chat.id)
    else:
        logger.warning(f'Function change language cannot recognise key {call.data}')


@bot.callback_query_handler(func=lambda call: call.data.startswith('money'))
def buttons_catcher_money(call):
    logger.info(f'Function {buttons_catcher_money.__name__} called and use arg: '
                f'user_id{call.from_user.id} and data: {call.data}')
    bot.answer_callback_query(call.id)

    if call.data.endswith('RUB'):
        set_settings(user_id=call.from_user.id, key='currency', value='RUB')
    elif call.data.endswith('USD'):
        set_settings(user_id=call.from_user.id, key='currency', value='USD')
    elif call.data.endswith('EUR'):
        set_settings(user_id=call.from_user.id, key='currency', value='EUR')
    elif call.data.endswith('cancel'):
        main_menu(user_id=call.from_user.id, command='start', chat_id=call.message.chat.id)
    else:
        logger.warning(f'Function change currency cannot recognise key {call.data}')

    reply = interface['responses']['saved'][get_settings(call.from_user.id, key='language')]
    bot.send_message(call.message.chat.id, reply)
    main_menu(user_id=call.from_user.id, command='settings', chat_id=call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('lang'))
def buttons_catcher_language(call):
    logger.info(f'Function {buttons_catcher_language.__name__} called and use arg: '
                f'user_id{call.from_user.id} and data: {call.data}')
    bot.answer_callback_query(call.id)

    if call.data.endswith('cancel'):
        main_menu(user_id=call.from_user.id, command='settings', chat_id=call.message.chat.id)
    else:
        set_settings(user_id=call.from_user.id, key='language', value=call.data[9:])

    reply = interface['responses']['saved'][call.data[9:]]
    bot.send_message(call.message.chat.id, reply)
    main_menu(user_id=call.from_user.id, command='settings', chat_id=call.message.chat.id)


def main_menu(user_id, command, chat_id):
    logger.info(f'Function {main_menu.__name__} called '
                f'and use argument: user_id {user_id} key {command} chat_id {chat_id}')
    lang = get_settings(user_id, key='language')
    if command == 'start':
        reply = start_reply(
                first_name=get_settings(user_id=user_id,key='first_name'),
                last_name=get_settings(user_id=user_id,key='last_name'),
                status=get_navigate(user_id),
                language=lang
            )
        bot.send_message(chat_id, reply, reply_markup=main_menu_keyboard)
    elif command == 'settings':
        set_settings(user_id=user_id, key='status', value='old')
        check_user_in_redis(user_id)
        logger.info(f'"settings" command is called with {user_id}')
        set_navigate(user_id, value='sett') # а надо ли?
        reply = settings_reply(
            language=lang,
            currency=get_settings(user_id, key='currency')
        )
        bot.send_message(chat_id, reply, reply_markup=settings_keyboard)
    elif command == 'history':
        # проверка на нюфага
        # set_settings(msg=call, key='command', value='history')
        # get_history()
        pass
    elif command in ['lowprice', 'highprice', "bestdeal"]:
        set_settings(user_id=user_id, key='status', value='old')
        set_settings(user_id=user_id, key='command', value=command)
        set_navigate(user_id=user_id, value='city_h')
        make_dialogue(user_id=user_id, command=command, chat_id=chat_id)


def make_dialogue(user_id, command, chat_id):
    logger.info(f'Function {make_dialogue.__name__} called and use argument: '
                f'user_id {user_id}  key {command}')

    language = get_settings(user_id= user_id, key='language')
    # order = get_settings(user_id= user_id, key='order')
    status = get_navigate(user_id= user_id)
    reply = interface['errors']['input'][language]

    if status == 'city_h':
        reply = interface['questions']['city'][language]
        bot.register_next_step_handler(bot.send_message(chat_id, reply), choose_city)
    elif status == 'count_h':
        reply = interface['questions']['count'][language] + '20'
        bot.send_message(chat_id, reply)
    elif status == 'count_p':
        reply = interface['questions']['need_photo'][language]
        bot.send_message(chat_id, reply, reply_markup=photo_keyboard)


def choose_city(message):
    logger.info(f'function {choose_city.__name__} was called')
    language = get_settings(user_id=message.from_user.id, key='language')
    # chat_id = message.chat.id
    # chat_id = call.message.chat.id # id чата
    # user_id = call.from_user.id
    # user_id = message.from_user.id # id юзера

    if message.text.strip().replace(' ', '').replace('-', '').isalpha():
        locations = make_locations_list(message)
        logger.info(f'Location return: {locations}')
        if not locations or len(locations) < 1:
            bot.send_message(message.chat.id, interface['errors']['count'][language])
        elif locations.get('bad_request'):
            bot.send_message(message.chat.id, interface['errors']['bad_request'][language])
        else:
            menu = telebot.types.InlineKeyboardMarkup()
            for loc_name, loc_id in locations.items():
                menu.add(telebot.types.InlineKeyboardButton(
                    text=loc_name,
                    callback_data='code' + loc_id)
                )
            bot.send_message(message.chat.id, interface['questions']['loc_choose'][language], reply_markup=menu)
    else:
        bot.send_message(message.chat.id, interface['errors']['city'][get_settings(
            user_id=message.from_user.id,
            key='language')
        ])
        make_dialogue(user_id=message.from_user.id, command='city_h', chat_id=message.chat.id)
#

# def get_locations(message):
#
#     user_id = message.from_user.id
#     language = get_settings(msg=message, key='language')
#     locations = make_locations_list(message)
#     logger.info(f'Function {get_locations.__name__} called and use argument user_id : {user_id}')
#
    # if not locations or len(locations) < 1:
    #     bot.send_message(user_id, interface['errors']['count'][language])
    # elif locations.get('bad_request'):
    #     bot.send_message(user_id, interface['errors']['bad_request'][language])
    # else:
    #     menu = telebot.types.InlineKeyboardMarkup()
    #     for loc_name, loc_id in locations.items():
    #         menu.add(telebot.types.InlineKeyboardButton(
    #                 text=loc_name,
    #                 callback_data='code' + loc_id)
    #             )
    #     bot.send_message(user_id, interface['questions']['loc_choose'][language], reply_markup=menu)
#         #тут надо отловить нажатие кнопки в списке локаций
# @bot.callback_query_handler(func=lambda call: call.data.startswith('photo'))
# def photo_handler(call):
#
#
#     bot.answer_callback_query(call.id)
#
#     user_id = call.from_user.id
#     language = get_settings(msg=call, key='language')
#     logger.info(f'Function {photo_handler.__name__} called and use argument: '
#                 f'user_id {user_id} and call data {call.data}')
#     if call.data.endswith('yes'):
#         bot.send_message(user_id, interface['questions']['photo'][language])
#     else:
#         set_settings(msg=call, key='photo_count', value=0)
#         set_navigate(msg=call, value='date')
#         choose_date_1(call)
#
#
#
#
#
# @bot.message_handler(content_types=['text'])
# def text_reply(message):
#
#     """
#     Тут обработчик текстовых ответов на вопросы о цене, радиусе поиска, городе
#     :param message:
#     :return:
#     """
#     user_id = message.from_user.id
#     language = get_settings(msg=message, key='language')
#     status = get_navigate(msg=message)
#     logger.info(f'Function {text_reply.__name__} called and use argument user_id : {user_id}')
#
#     if status == 'date':
#         choose_date_1(message)
#     elif status == "city_h":
#         if message.text.strip().replace(' ', '').replace('-', '').isalpha():
#             get_locations(message)
#         else:
#             bot.send_message(user_id, interface['errors']['city'][language])
#         make_dialogue(message)
#     elif status == 'count_h':
#         if ' ' not in message.text.strip() and message.text.strip().isdigit() and 0 < int(message.text.strip()) <= 20:
#             set_settings(msg=message, key='hotel_count', value=message.text.strip())
#             set_navigate(msg=message, value='count_p')
#             bot.send_message(user_id, interface['responses']['ok'][language])
#         else:
#             bot.send_message(user_id, interface['errors']['count'][language])
#         make_dialogue(message)
#     elif status == 'count_p':
#         if ' ' not in message.text.strip() and message.text.strip().isdigit() and 0 < int(message.text.strip()) <= 5:
#             set_settings(msg=message, key='photo_count', value=message.text.strip())
#             bot.send_message(user_id, interface['responses']['ok'][language])
#             set_navigate(msg=message, value='date')
#             choose_date_1(message)
#
#         else:
#             bot.send_message(user_id, interface['errors']['count'][language])
#             make_dialogue(message)
#
#
#
# def choose_date_1(message):
#     logger.info(f'Function {choose_date_1.__name__} called')
#
#     language = get_settings(msg=message, key='language')
#     reply = interface['questions']['date1'][language]
#     calendar, step = DetailedTelegramCalendar(calendar_id=1, locale=language).build()
#     bot.send_message(message.chat.id, f"{reply} {LSTEP[step]}", reply_markup=calendar)
#
#
# def choose_date_2(message):
#     logger.info(f'Function {choose_date_2.__name__} called')
#
#     language = get_settings(msg=message, key='language')
#     reply = interface['questions']['date2'][language]
#     calendar, step = DetailedTelegramCalendar(calendar_id=2, locale=language).build()
#     bot.send_message(message.chat.id, f"{reply} {LSTEP[step]}", reply_markup=calendar)
#
#
# @bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
# def callback_calendar(call):
#     logger.info(f'Function {callback_calendar.__name__} called ')
#
#     result, key, step = DetailedTelegramCalendar(calendar_id=1).process(call.data)
#     if not result and key:
#         bot.edit_message_text(f"Calendar 1: Select {LSTEP[step]}", call.message.chat.id, call.message.message_id,
#                               reply_markup=key)
#     elif result:
#         bot.edit_message_text(f"You selected {result} in calendar 1", call.message.chat.id,call.message.message_id)
#         y, m, d = [int(i) for i in str(result).split('-')]
#         result = get_timestamp(y, m, d)
#         set_settings(msg=call, key='date1', value=result)
#         choose_date_2(call.message)
#
#
# @bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
# def callback_calendar(call):
#     logger.info(f'Function {callback_calendar.__name__} called')
#
#     result, key, step = DetailedTelegramCalendar(calendar_id=2).process(call.data)
#
#     if not result and key:
#         bot.edit_message_text(f"Calendar 2: Select {LSTEP[step]}", call.message.chat.id, call.message.message_id,
#                               reply_markup=key)
#     elif result:
#         first_date = get_settings(msg=call, key='date1')
#         y, m, d = [int(i) for i in str(result).split('-')]
#         second_date = get_timestamp(y, m, d)
#
#         if float(first_date) >= float(second_date):
#             bot.send_message(call.message.chat.id, 'неправильная дата')
#             set_settings(msg=call, key='date1', value=' ')
#             choose_date_1(call.message)
#         else:
#             bot.edit_message_text(f"You selected {result} in calendar 2", call.message.chat.id,call.message.message_id)
#             set_settings(msg=call, key='date2', value=second_date)
#             # set_navigate()
#             hotel_result(call)
#
#
#
# def get_locations(message):
#
#     user_id = message.from_user.id
#     language = get_settings(msg=message, key='language')
#     locations = make_locations_list(message)
#     logger.info(f'Function {get_locations.__name__} called and use argument user_id : {user_id}')
#
#     if not locations or len(locations) < 1:
#         bot.send_message(user_id, interface['errors']['count'][language])
#     elif locations.get('bad_request'):
#         bot.send_message(user_id, interface['errors']['bad_request'][language])
#     else:
#         menu = telebot.types.InlineKeyboardMarkup()
#         for loc_name, loc_id in locations.items():
#             menu.add(telebot.types.InlineKeyboardButton(
#                     text=loc_name,
#                     callback_data='code' + loc_id)
#                 )
#         bot.send_message(user_id, interface['questions']['loc_choose'][language], reply_markup=menu)
#         #тут надо отловить нажатие кнопки в списке локаций
#
#
# @bot.callback_query_handler(func=lambda call: True)
# def hotel_handler(call):
#     logger.info(f'Function {hotel_handler.__name__} called ')
#
#     language = get_settings(msg=call, key='language')
#     set_settings(msg=call, key='city', value=call.data)
#     status = get_navigate(msg=call)
#     bot.answer_callback_query(call.id)
#     bot.edit_message_text(interface['responses']['ok'][language], call.message.chat.id, call.message.message_id)
#     set_navigate(msg=call, value='count_h')
#     make_dialogue(call)
#
#
# def hotel_result(message):
#
#     user_id = message.from_user.id
#     logger.info(f'Function {hotel_result.__name__} called and use argument user_id : {user_id}')
#
#     # тут происходит магия поиска и возврата отелей
#     result = 'ссылка1*ссылка2*ссылка*3'
#     # тут происходит магия показа отелей
#     set_navigate(msg=message, value='main')
#     print(get_settings(msg=message))
#     set_history(user_id, result)
#     bot.send_message(user_id, 'дно достигнуто')
#
#
# def get_history(call):
#     user_id = call.from_user.id
#     ans = get_history_from_db(user_id)
#     for i_element in ans:
#         pass
#     bot.send_message(user_id, ans)





bot.infinity_polling()
