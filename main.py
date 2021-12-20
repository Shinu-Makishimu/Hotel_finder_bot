import telebot.types
from loguru import logger
from telebot import TeleBot
from settings import API_TOKEN, NAME_DATABASE, logger_config, commands_list

from accessory import get_timestamp, check_dates

import database as db
from keyboard import settings_keyboard, main_menu_keyboard, language_keyboard, money_keyboard
from language import interface
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from os import path
from bot_requests.locations import make_locations_list
from bot_requests.hotels import get_hotels
from bot_requests.menu import start_reply, settings_reply

bot = TeleBot(API_TOKEN)
logger.configure(**logger_config)
logger.info("\n" + "\\" * 50 + 'new session started' + "//" * 50 + "\n")

if not path.isfile(NAME_DATABASE):
    db.create_bd_if_not_exist()


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


@bot.message_handler(commands=['start', 'lowprice', 'highprice', 'bestdeal', 'settings', 'help'])
def commands_catcher(message):
    """
    отлов команд
    :param message:
    :return:
    """
    logger.info(f'Function {commands_catcher.__name__} called '
                f'and use argument: {message.text}')
    if message.text == commands_list[0]:
        db.kill_user(message.from_user.id)
        db.create_user_in_redis(
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
        db.set_navigate(user_id=call.from_user.id, value='main')
        main_menu(user_id=call.from_user.id, command='start', chat_id=call.message.chat.id)
    else:
        logger.warning(f'Function change language cannot recognise key {call.data}')


@bot.callback_query_handler(func=lambda call: call.data.startswith('money'))
def buttons_catcher_money(call):
    logger.info(f'Function {buttons_catcher_money.__name__} called and use arg: '
                f'user_id{call.from_user.id} and data: {call.data}')
    bot.answer_callback_query(call.id)

    if call.data.endswith('RUB'):
        db.set_settings(user_id=call.from_user.id, key='currency', value='RUB')
    elif call.data.endswith('USD'):
        db.set_settings(user_id=call.from_user.id, key='currency', value='USD')
    elif call.data.endswith('EUR'):
        db.set_settings(user_id=call.from_user.id, key='currency', value='EUR')
    elif call.data.endswith('cancel'):
        main_menu(user_id=call.from_user.id, command='start', chat_id=call.message.chat.id)
    else:
        logger.warning(f'Function change currency cannot recognise key {call.data}')

    reply = interface['responses']['saved'][db.get_settings(call.from_user.id, key='language')]
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
        db.set_settings(user_id=call.from_user.id, key='language', value=call.data[9:])

    reply = interface['responses']['saved'][call.data[9:]]
    bot.send_message(call.message.chat.id, reply)
    main_menu(user_id=call.from_user.id, command='settings', chat_id=call.message.chat.id)


def main_menu(user_id, command, chat_id):
    logger.info(f'Function {main_menu.__name__} called '
                f'and use argument: user_id {user_id} key {command} chat_id {chat_id}')
    lang = db.get_settings(user_id, key='language')
    if command == 'start':
        reply = start_reply(
            first_name=db.get_settings(user_id=user_id, key='first_name'),
            last_name=db.get_settings(user_id=user_id, key='last_name'),
            status=db.get_navigate(user_id),
            language=lang
        )
        bot.send_message(chat_id, reply, reply_markup=main_menu_keyboard)
    elif command == 'settings':
        db.set_settings(user_id=user_id, key='status', value='old')
        db.check_user_in_redis(user_id)
        logger.info(f'"settings" command is called with {user_id}')
        db.set_navigate(user_id, value='sett')  # а надо ли?
        reply = settings_reply(
            language=lang,
            currency=db.get_settings(user_id, key='currency')
        )
        bot.send_message(chat_id, reply, reply_markup=settings_keyboard)
    elif command == 'history':
        # проверка на нюфага
        # set_settings(msg=call, key='command', value='history')
        # get_history()
        pass
    elif command in ['lowprice', 'highprice', "bestdeal"]:
        db.set_settings(user_id=user_id, key='status', value='old')
        db.set_settings(user_id=user_id, key='command', value=command)
        bot.register_next_step_handler(bot.send_message(chat_id,
                                                        interface['questions']['city'][lang]),
                                       choose_city
                                       )


def choose_city(message):
    logger.info(f'function {choose_city.__name__} was called')
    language = db.get_settings(user_id=message.from_user.id, key='language')

    if message.text.strip().replace(' ', '').replace('-', '').isalpha():
        locations = make_locations_list(message)
        logger.info(f'Location return: {locations}')
        if not locations or len(locations) < 1:
            bot.send_message(message.chat.id, interface['errors']['city_not_found'][language])
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
        bot.send_message(message.chat.id, interface['errors']['city'][language])
        bot.register_next_step_handler(bot.send_message(message.chat.id,
                                                        interface['questions']['city'][language]),
                                       choose_city)


@bot.callback_query_handler(func=lambda call: call.data.startswith('code'))
def city_buttons_catcher(call):
    logger.info(f'Function {city_buttons_catcher.__name__} called and use arg: '
                f'user_id {call.from_user.id} and data: {call.data}')
    bot.answer_callback_query(call.id)
    db.set_settings(user_id=call.from_user.id, key='city', value=call.data[4:])
    bot.send_message(call.message.chat.id,
                     interface['responses']['saved'][db.get_settings(call.from_user.id, key='language')])
    msg = bot.send_message(call.message.chat.id,
                           interface['questions']['count'][db.get_settings(call.from_user.id, key='language')])
    bot.register_next_step_handler(msg, hotel_counter)


def hotel_counter(message):
    if ' ' not in message.text.strip() and message.text.strip().isdigit() and 0 < int(message.text.strip()) <= 20:
        logger.info(f'Function {hotel_counter.__name__} called, user input is in condition. use arg: '
                    f'hotel counter =  {message.text}')
        db.set_settings(user_id=message.from_user.id, key='hotel_count', value=message.text.strip())
        msg = bot.send_message(message.chat.id,
                               interface['questions']['photo'][db.get_settings(message.from_user.id, key='language')] +
                               '0 - 5')
        bot.register_next_step_handler(msg, photo_counter_answ)
    else:
        logger.info(f'Function {hotel_counter.__name__} called, user input IS NOT in  condition.')
        msg = bot.send_message(message.chat.id,
                               interface['questions']['count'][db.get_settings(message.from_user.id, key='language')])
        bot.register_next_step_handler(msg, hotel_counter)


def photo_counter_answ(message):
    logger.info(f'Function {photo_counter_answ.__name__} called, user input is in condition. use arg: '
                f'{message.text}')
    if message.text.strip().isdigit() and 0 <= int(message.text.strip()) <= 5:
        db.set_settings(user_id=message.from_user.id, key='photo_count', value=message.text)
        choose_date(message)
    else:
        msg = bot.send_message(message.message.chat.id,
                               interface['questions']['photo'][db.get_settings(message.from_user.id, key='language')] +
                               '0 - 5')
        bot.register_next_step_handler(msg, photo_counter_answ)


def choose_date(message):
    logger.info(f'\n\n{message}\n\n')
    date_1 = db.get_settings(user_id=message.from_user.id, key='date1')
    date_2 = db.get_settings(user_id=message.from_user.id, key='date2')
    language = db.get_settings(user_id=message.from_user.id, key='language')
    logger.info(f'Function {choose_date.__name__} called with args:'
                f' date_1 = {date_1} date_2 = {date_2} language {language}')
    if date_1 == 0 or date_1 is None:
        reply = interface['questions']['date1'][language]
        calendar, step = DetailedTelegramCalendar(calendar_id=1, locale=language[:2]).build()
        bot.send_message(message.chat.id, f"{reply} {LSTEP[step]}", reply_markup=calendar)
    else:  # date_2 == 0:
        reply = interface['questions']['date2'][language]
        calendar, step = DetailedTelegramCalendar(calendar_id=2, locale=language[:2]).build()
        bot.send_message(message.message.chat.id, f"{reply} {LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def callback_calendar_1(call):
    # {LSTEP[step]}
    logger.info(f'Function {callback_calendar_1.__name__} called ')
    result, key, step = DetailedTelegramCalendar(calendar_id=1).process(call.data)
    language = db.get_settings(user_id=call.from_user.id, key='language')
    if not result and key:
        bot.edit_message_text(interface['questions']['date1'][language], call.message.chat.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(interface['responses']['check_in'][language] + '\n' + str(result), call.message.chat.id,
                              call.message.message_id)
        result = get_timestamp(result)
        db.set_settings(user_id=call.from_user.id, key='date1', value=result)
        db.set_settings(user_id=call.from_user.id, key='date2', value=0)
        choose_date(call)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def callback_calendar_2(call):
    logger.info(f'Function {callback_calendar_2.__name__} called')
    language = db.get_settings(user_id=call.from_user.id, key='language')
    result, key, step = DetailedTelegramCalendar(calendar_id=2).process(call.data)

    if not result and key:
        bot.edit_message_text(interface['questions']['date2'][language], call.message.chat.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        if check_dates(check_in=db.get_settings(user_id=call.from_user.id, key='date1'),
                       check_out=get_timestamp(result)):
            bot.edit_message_text(interface['responses']['check_out'][language] + '\n' + str(result),
                                  call.message.chat.id,
                                  call.message.message_id)
            result = get_timestamp(result)
            db.set_settings(user_id=call.from_user.id, key='date2', value=result)
            hotel_result(call)
        else:
            db.set_settings(user_id=call.from_user.id, key='date1', value=0)
            db.set_settings(user_id=call.from_user.id, key='date2', value=0)
            choose_date(call)


def hotel_result(call):
    command = db.get_settings(user_id=call.from_user.id, key='command')
    logger.info(f'Function {hotel_result.__name__} called and use argument command : {command}')

    if command == 'bestdeal':
        msg = bot.send_message(call.message.chat.id,
                               interface['questions']['radius'][db.get_settings
                               (user_id=call.from_user.id, key='language')])
        bot.register_next_step_handler(msg, distanse_from_centre)
    elif command in ['lowprice', 'highprice']:
        end_conversation(user_id=call.from_user.id, chat_id=call.message.chat.id)


def distanse_from_centre(message):
    logger.info(f'Function {distanse_from_centre.__name__} called, user input is in condition. use arg: '
                f'distance =  {message.text}')
    if message.text.strip().isdigit():
        db.set_settings(user_id=message.from_user.id, key='distance', value=message.text.strip())
        msg = bot.send_message(message.chat.id,
                               interface['questions']['price'][db.get_settings(message.from_user.id, key='language')])
        bot.register_next_step_handler(msg, photo_counter_answ)
    else:
        logger.info(f'Function {distanse_from_centre.__name__} called, user input IS NOT in  condition.')
        msg = bot.send_message(message.chat.id,
                               interface['questions']['radius'][db.get_settings(message.from_user.id, key='language')])
        bot.register_next_step_handler(msg, distanse_from_centre)


def min_max_price(message):
    logger.info(f'Function {min_max_price.__name__} called, user input is in condition. use arg: '
                f'distance =  {message.text} user_id {message.from_user.id}')
    if message.replace(' ', '').isdigit() and len(message.split()) == 2:
        min_price, max_price = sorted(message.text.strip().split(), key=int)
        logger.info(f'min pr {min_price}, max pr {max_price}')
        db.set_settings(user_id=message.from_user.id, key='min_price', value=min_price)
        db.set_settings(user_id=message.from_user.id, key='max_price', value=max_price)

    else:
        logger.info(f'Function {min_max_price.__name__} called, user input IS NOT in  condition.')
        msg = bot.send_message(message.chat.id,
                               interface['questions']['price'][db.get_settings(message.from_user.id, key='language')])
        bot.register_next_step_handler(msg, min_max_price)


def end_conversation(user_id, chat_id):
    hotels = get_hotels(user_id=user_id)
    logger.info(f'Function {get_hotels.__name__} returned: {hotels}')
    db.set_history(user_id, hotels)
    if not hotels or len(hotels) < 1:
        bot.send_message(chat_id, interface['errors']['hotels'][db.get_settings
                                                                                (user_id=user_id, key='language')])
    elif 'bad_request' in hotels:
        bot.send_message(chat_id, interface['errors']['bad_request'][db.get_settings
                                                                                (user_id=user_id, key='language')])
    else:
        bot.send_message(chat_id, interface['responses']['hotels_found'][db.get_settings(user_id=user_id, key='language')] + str(len(hotels)))
        for hotel in hotels:
            bot.send_message(chat_id, hotel)


bot.infinity_polling()
