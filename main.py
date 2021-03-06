from os import path
from time import sleep
from loguru import logger
from telebot import TeleBot, types
from datetime import datetime, date
from telegram_bot_calendar import DetailedTelegramCalendar

import accessory
import keyboard as kb
import database as db
import settings as sett
from language import interface
from bot_requests import hotels_finder, locations, menu


bot = TeleBot(sett.API_TOKEN)
logger.configure(**sett.logger_config)
logger.info("\n" + "\\" * 50 + 'new session started' + "//" * 50 + "\n")

if not path.isfile(sett.NAME_DATABASE):
    db.create_bd_if_not_exist()


@bot.message_handler(commands=['start', 'lowprice', 'highprice', 'bestdeal', 'settings', 'help'])
def commands_catcher(message: types.Message) -> None:
    """
    Функция ловит введённые команды пользователя и перенапраяляет в main menu
    :param message: сообщение
    :return: None
    """
    logger.info(f'Function {commands_catcher.__name__} called '
                f'and use argument: {message.text}')
    if message.text == sett.commands_list[0]:
        db.kill_user(message.from_user.id)
        db.create_user_in_redis(
            user_id=str(message.from_user.id),
            language=message.from_user.language_code,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        logger.info(f'"start" command is called')
        main_menu(
            user_id=str(message.from_user.id),
            command=message.text.strip('/'),
            chat_id=message.chat.id,
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('help'))
def buttons_catcher_help(call: types.CallbackQuery) -> None:
    """
    Функция обрабатывает нажатие клавиш клавиатуры help
    :param call: Callback
    :return: None
    """
    logger.info(f'Function {buttons_catcher_help.__name__} was called with {call.data}')
    lang = db.get_settings(user_id=call.from_user.id, key='language')
    bot.answer_callback_query(call.id)
    if call.data.endswith('low'):
        bot.send_message(
            chat_id=call.message.chat.id,
            text=interface['responses']['help_l'][lang]
        )
    elif call.data.endswith('high'):
        bot.send_message(
            chat_id=call.message.chat.id,
            text=interface['responses']['help_h'][lang]
        )
    elif call.data.endswith('sett'):
        bot.send_message(
            chat_id=call.message.chat.id,
            text=interface['responses']['help_s'][lang]
        )
    elif call.data.endswith('best'):
        bot.send_message(
            chat_id=call.message.chat.id,
            text=interface['responses']['help_b'][lang]
        )
    else:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        main_menu(
            user_id=str(call.from_user.id),
            command='start',
            chat_id=call.message.chat.id
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('main'))
def buttons_catcher_main(call: types.CallbackQuery) -> None:
    """
    Функция обрабатывает нажатые кнопки инлайн клавиатуры главного меню
    :param call: Callback
    :return: None
    """
    logger.info(f'Function {buttons_catcher_main.__name__} called and use arg: '
                f'user_id{call.from_user.id} and data: {call.data}')
    bot.answer_callback_query(call.id)
    main_menu(
        user_id=str(call.from_user.id),
        command=call.data.split('_')[1],
        chat_id=call.message.chat.id
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('set'))
def buttons_catcher_settings(call: types.CallbackQuery) -> None:
    """
    Функция обрабатывает нажатые кнопки инлайн клавиатуры меню настроек
    :param call: Callback
    :return: None
    """
    logger.info(f'Function {buttons_catcher_settings.__name__} called and use arg: '
                f'user_id{call.from_user.id} and data: {call.data}')
    logger.info(f'Function settings menu called')
    bot.answer_callback_query(call.id)
    lang = db.get_settings(user_id=call.from_user.id, key='language')

    if call.data == 'set_money':
        bot.send_message(
            chat_id=call.message.chat.id,
            text=interface['responses']['ask_to_select'][lang],
            reply_markup=kb.money_keyboard
        )
    elif call.data == 'set_language':
        bot.send_message(
            chat_id=call.message.chat.id,
            text=interface['responses']['ask_to_select'][lang],
            reply_markup=kb.language_keyboard
        )
    elif call.data == 'set_back':
        db.set_navigate(user_id=call.from_user.id, value='main')
        main_menu(
            user_id=str(call.from_user.id),
            command='start',
            chat_id=call.message.chat.id
        )
    else:
        logger.warning(f'Function change language cannot recognise key {call.data}')


@bot.callback_query_handler(func=lambda call: call.data.startswith('money'))
def buttons_catcher_money(call: types.CallbackQuery) -> None:
    """
    Функция обрабатывает нажатые кнопки инлайн клавиатуры меню смены денежной еденицы
    :param call: Callback
    :return: None
    """
    logger.info(f'Function {buttons_catcher_money.__name__} called and use arg: '
                f'user_id{call.from_user.id} and data: {call.data}')
    bot.answer_callback_query(call.id)

    if call.data.endswith('RUB'):
        db.set_settings(
            user_id=call.from_user.id,
            key='currency',
            value='RUB'
        )
    elif call.data.endswith('USD'):
        db.set_settings(
            user_id=call.from_user.id,
            key='currency',
            value='USD'
        )
    elif call.data.endswith('EUR'):
        db.set_settings(
            user_id=call.from_user.id,
            key='currency',
            value='EUR'
        )
    elif call.data.endswith('cancel'):
        main_menu(
            user_id=str(call.from_user.id),
            command='start',
            chat_id=call.message.chat.id
        )
    else:
        logger.warning(f'Function change currency cannot recognise key {call.data}')

    reply = interface['responses']['saved'][db.get_settings(call.from_user.id, key='language')]
    bot.send_message(call.message.chat.id, reply)
    main_menu(
        user_id=str(call.from_user.id),
        command='settings',
        chat_id=call.message.chat.id
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('lang'))
def buttons_catcher_language(call: types.CallbackQuery) -> None:
    """
    Функция обрабатывает нажатые кнопки инлайн клавиатуры смены языка интерфейса
    :param call: Callback
    :return: None
    """
    logger.info(f'Function {buttons_catcher_language.__name__} called and use arg: '
                f'user_id{call.from_user.id} and data: {call.data}')
    bot.answer_callback_query(call.id)

    if call.data.endswith('cancel'):
        main_menu(
            user_id=str(call.from_user.id),
            command='settings',
            chat_id=call.message.chat.id
        )
    else:
        db.set_settings(
            user_id=call.from_user.id,
            key='language',
            value=call.data[9:]
        )

    reply = interface['responses']['saved'][call.data[9:]]
    bot.send_message(call.message.chat.id, reply)
    main_menu(
        user_id=str(call.from_user.id),
        command='settings',
        chat_id=call.message.chat.id
    )


def main_menu(user_id: str, command: str, chat_id: int) -> None:
    """
    функция формирующая главное меню, меню настроек и вызывает функции соответствующие нажатым кнопкам
    :param user_id: пользовательский id
    :param command: команда, которую выбрал пользователь
    :param chat_id: id чата, в который отправлять сообщения
    :return: None
    """
    logger.info(f'Function {main_menu.__name__} called '
                f'and use argument: user_id {user_id} key {command} chat_id {chat_id}')
    lang = db.get_settings(user_id, key='language')
    if command in ['start', 'another_one']:
        if command == 'another_one':
            reply = interface['responses']['another_one'][lang]
        else:
            reply = menu.start_reply(
                first_name=db.get_settings(user_id=user_id, key='first_name'),
                last_name=db.get_settings(user_id=user_id, key='last_name'),
                status=db.get_navigate(user_id),
                language=lang
            )
        bot.send_message(
            chat_id=chat_id,
            text=reply,
            reply_markup=kb.main_menu_keyboard
        )
    elif command == 'settings':
        db.set_settings(user_id=user_id, key='status', value='old')
        db.check_user_in_redis(user_id)
        logger.info(f'"settings" command is called with {user_id}')
        db.set_navigate(user_id, value='sett')  # а надо ли?

        reply = menu.settings_reply(
            language=lang,
            currency=db.get_settings(user_id, key='currency')
        )
        bot.send_message(chat_id, reply, reply_markup=kb.settings_keyboard)
    elif command == 'history':
        status = db.get_settings(user_id, key='status')
        if status == 'new':
            msg = bot.send_message(chat_id=chat_id, text='no_history')
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=interface['errors']['no_history'][lang]
            )
            sleep(3)
            bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        else:
            search_list = db.get_history_from_db(user_id=user_id, short=True)
            history_menu = types.InlineKeyboardMarkup()
            for search_string in search_list:
                history_menu.add(
                    types.InlineKeyboardButton(
                        text=search_string[2],
                        callback_data='history' + str(search_string[0])
                    )
                )
            history_menu.add(types.InlineKeyboardButton(text='back', callback_data='history_back_1'))
            bot.send_message(
                chat_id=chat_id,
                text= interface['elements']['city_list'][lang],
                reply_markup=history_menu
            )
    elif command in ['lowprice', 'highprice', "bestdeal"]:
        db.set_settings(user_id=user_id, key='status', value='old')
        db.set_settings(user_id=user_id, key='command', value=command)
        bot.send_message(
            chat_id=chat_id,
            text=interface['responses'][command][lang]
        )
        bot.register_next_step_handler(
            bot.send_message(
                chat_id=chat_id,
                text=interface['questions']['city'][lang]),
            choose_city
        )
    elif command == 'help':
        help_kb = kb.help_keyboard
        bot.send_message(
            chat_id=chat_id,
            text=interface['responses']['help'][db.get_settings(user_id=user_id, key='language')],
            reply_markup=help_kb,
            parse_mode='HTML')
    else:
        bot.send_message(chat_id=chat_id, text=interface['errors']['input'][lang])


@bot.callback_query_handler(func=lambda call: call.data.startswith('history'))
def history_button_catcher(call: types.CallbackQuery) -> None:
    """
    Функция обрабатывает нажатые кнопки меню истории
    :param call: Callback
    :return: None
    """
    logger.info(f'Function {history_button_catcher.__name__} called and use arg: '
                f'user_id {call.from_user.id} and data: {call.data}')

    bot.answer_callback_query(call.id)
    user_id = str(call.from_user.id)
    chat_id = call.message.chat.id
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data.endswith('back_1'):
        main_menu(user_id=user_id, chat_id=chat_id, command='start')
    elif call.data.endswith('back_2'):
        main_menu(user_id=user_id, chat_id=chat_id, command='history')
    elif call.data.endswith('go_search'):
        db.prepare_history_for_search(user_id=user_id)
        end_conversation(user_id, chat_id)
    else:
        db.get_settings(user_id=user_id, key='history_id', remove_kebab=True)
        lang = db.get_settings(call.from_user.id, key='language')
        history = db.get_history_from_db(user_id=user_id)
        search_record = ()
        for i_rec in range(len(history)):
            if int(history[i_rec][0]) == int(call.data[7:]):
                search_record = history[i_rec]
                db.set_settings(user_id=user_id, key='history_id', value=int(call.data[7:]))
        logger.info(f'search_rec is {search_record}')
        message = menu.history_reply(search_record, lang)
        history_menu = types.InlineKeyboardMarkup()
        history_menu.add(types.InlineKeyboardButton(text='Search again', callback_data='history_go_search'))
        history_menu.add(types.InlineKeyboardButton(text='back', callback_data='history_back_2'))

        bot.send_message(
            chat_id,
            text=interface['elements']['more_info'][lang] + message,
            reply_markup=history_menu)


def choose_city(message: types.Message) -> None:
    """
    Функция выбора города.
    :param message: Message
    :return: None
    """
    logger.info(f'function {choose_city.__name__} was called')
    db.clean_settings(user_id=message.from_user.id)
    language = db.get_settings(user_id=message.from_user.id, key='language')
    if message.text.strip().replace(' ', '').replace('-', '').isalpha():

        loc = locations.make_locations_list(message)
        logger.info(f'Location return: len= {len(loc)} values = {loc}')
        if not loc or len(loc) < 1:
            bot.send_message(message.chat.id, interface['errors']['city_not_found'][language])
        elif loc.get('bad_request'):
            bot.send_message(message.chat.id, interface['errors']['bad_request'][language])
        else:
            if len(loc) == 1:
                for loc_name, loc_id in loc.items():
                    db.set_settings(
                        user_id=message.from_user.id,
                        key='city',
                        value=loc_id
                    )
                    db.set_settings(
                        user_id=message.from_user.id,
                        key='city_name',
                        value=loc_name
                    )

                msg = bot.send_message(
                    message.chat.id,
                    interface['questions']['count'][db.get_settings(user_id=message.from_user.id, key='language')]
                )
                bot.register_next_step_handler(msg, hotel_counter)
            else:
                city_menu = types.InlineKeyboardMarkup()
                for loc_name, loc_id in loc.items():
                    city_menu.add(types.InlineKeyboardButton(
                        text=loc_name,
                        callback_data=f'code{loc_id}')
                    )
                    db.set_settings(user_id=message.from_user.id, key=loc_id, value=loc_name)
                city_menu.add(types.InlineKeyboardButton(
                    text=interface['buttons']['no_city'][language],
                    callback_data='code_red')
                )
                bot.send_message(
                    message.chat.id,
                    interface['questions']['loc_choose'][language],
                    reply_markup=city_menu
                )
    else:
        bot.send_message(message.chat.id, interface['errors']['city'][language])
        bot.register_next_step_handler(
            bot.send_message(
                message.chat.id,
                interface['questions']['city'][language]),
            choose_city
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('code'))
def city_buttons_catcher(call: types.CallbackQuery) -> None:
    """
    Функция, обрабатывающая нажатия кнопок городов.
    :param call: Callback
    :return: None
    """
    logger.info(f'Function {city_buttons_catcher.__name__} called and use arg: '
                f'user_id {call.from_user.id} and data: {call.data}')

    bot.answer_callback_query(call.id)
    lang = db.get_settings(call.from_user.id, key='language')
    if call.data == 'code_red':
        bot.register_next_step_handler(
            bot.send_message(
                call.message.chat.id,
                interface['questions']['city'][lang]), choose_city)
    else:
        db.set_settings(user_id=call.from_user.id, key='city', value=call.data[4:])
        city_name = db.get_settings(user_id=call.from_user.id, key=call.data[4:])
        db.set_settings(user_id=call.from_user.id, key='city_name', value=city_name)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        msg = bot.send_message(
            call.message.chat.id,
            interface['questions']['count'][lang]
        )
        bot.register_next_step_handler(msg, hotel_counter)


def hotel_counter(message: types.Message) -> None:
    """
    Функция обрабатывающая ответ пользователя на вопрос о количестве результатов выдачи поиска
    :param message: Message
    :return: None
    """
    if ' ' not in message.text.strip() and message.text.strip().isdigit() and 0 < int(message.text.strip()) <= 20:
        logger.info(f'Function {hotel_counter.__name__} called, user input is in condition. use arg: '
                    f'hotel counter =  {message.text}')
        db.set_settings(
            user_id=message.from_user.id,
            key='hotel_count',
            value=message.text.strip()
        )
        msg = bot.send_message(
            message.chat.id,
            interface['questions']['photo'][db.get_settings(message.from_user.id, key='language')]
        )
        bot.register_next_step_handler(msg, photo_counter_answer)
    else:
        logger.info(f'Function {hotel_counter.__name__} called, user input IS NOT in  condition.')
        msg = bot.send_message(
            message.chat.id,
            interface['questions']['count'][db.get_settings(message.from_user.id, key='language')]
        )
        bot.register_next_step_handler(msg, hotel_counter)


def photo_counter_answer(message: types.Message) -> None:
    """
    функция обрабатывающая количество фотографий для каждого результата поиска
    :param message: Message
    :return: None
    """
    logger.info(f'Function {photo_counter_answer.__name__} called, user input is in condition. use arg: '
                f'{message.text}')
    if message.text.strip().isdigit() and 0 <= int(message.text.strip()) <= 5:
        db.set_settings(
            user_id=message.from_user.id,
            key='photo_count',
            value=message.text
        )
        choose_date(message)
    else:
        msg = bot.send_message(
            message.chat.id,
            interface['questions']['photo'][db.get_settings(message.from_user.id, key='language')])
        bot.register_next_step_handler(msg, photo_counter_answer)


def choose_date(message: types.Message or types.CallbackQuery) -> None:
    """
    функция, формирующая меню выбора дат въезда/выезда
    :param message: Message or Cazllback
    :return:None
    """
    date_1 = db.get_settings(user_id=message.from_user.id, key='date1')
    date_2 = db.get_settings(user_id=message.from_user.id, key='date2')
    language = db.get_settings(user_id=message.from_user.id, key='language')

    logger.info(f'Function {choose_date.__name__} called with args:'
                f' date_1 = {date_1} date_2 = {date_2} language {language}')

    if date_1 == '0' or date_1 is None:
        reply = interface['questions']['date1'][language]
        calendar, step = DetailedTelegramCalendar(
            calendar_id=1,
            locale=language[:2],
            min_date=date.today()).build()
        try:
            # это очень нужно!
            bot.send_message(message.chat.id, f"{reply}", reply_markup=calendar)
        except Exception as e:
            logger.info(f'Поймана ошибка {e}')
            bot.send_message(message.message.chat.id, f"{reply}", reply_markup=calendar)
    else:
        min_date = datetime.fromtimestamp(float(date_1)).date()
        reply = interface['questions']['date2'][language]
        calendar, step = DetailedTelegramCalendar(calendar_id=2, locale=language[:2], min_date=min_date).build()
        bot.send_message(message.message.chat.id, f"{reply}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def callback_calendar_1(call: types.CallbackQuery) -> None:
    """
    функция обрабатывающая календарь чек ин
    :param call: Callback
    :return:None
    """
    # {LSTEP[step]}
    logger.info(f'Function {callback_calendar_1.__name__} called ')
    # result= key= step = ''
    result, key, step = DetailedTelegramCalendar(calendar_id=1).process(call.data)
    lang = db.get_settings(user_id=call.from_user.id, key='language')

    if not result and key:
        bot.edit_message_text(
            interface['questions']['date1'][lang],
            call.message.chat.id,
            call.message.message_id,
            reply_markup=key
        )
    elif result:
        if result < datetime.now().date():
            db.get_settings(user_id=call.from_user.id, key='date1', remove_kebab=True)
            bot.edit_message_text(
                text=interface['errors']['back_to_the_past'][lang],
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
            choose_date(call)
        else:
            logger.info(f' нормальный запрос')
            bot.edit_message_text(
                interface['responses']['check_in'][lang] + '\n' + str(result),
                call.message.chat.id,
                call.message.message_id
            )
            result = accessory.get_timestamp(result)
            db.set_settings(user_id=call.from_user.id, key='date1', value=result)
            db.set_settings(user_id=call.from_user.id, key='date2', value="0")
            choose_date(call)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def callback_calendar_2(call: types.CallbackQuery) -> None:
    """
    Фнкция обрабатывающая календарь чекаута
    :param call: Callback
    :return: None
    """
    logger.info(f'Function {callback_calendar_2.__name__} called')
    language = db.get_settings(user_id=call.from_user.id, key='language')
    result, key, step = DetailedTelegramCalendar(calendar_id=2).process(call.data)

    if not result and key:
        bot.edit_message_text(
            interface['questions']['date2'][language],
            call.message.chat.id,
            call.message.message_id,
            reply_markup=key
        )
    elif result:
        if accessory.check_dates(
                check_in=int(db.get_settings(user_id=call.from_user.id, key='date1')),
                check_out=accessory.get_timestamp(result)):

            bot.edit_message_text(
                interface['responses']['check_out'][language] + '\n' + str(result),
                call.message.chat.id,
                call.message.message_id
            )
            result = accessory.get_timestamp(result)
            db.set_settings(user_id=call.from_user.id, key='date2', value=result)

            if db.get_settings(user_id=call.from_user.id, key='command') not in ['lowprice', 'highprice']:
                msg = bot.send_message(
                    call.message.chat.id,
                    interface['questions']['radius'][db.get_settings(
                        user_id=call.from_user.id,
                        key='language')]
                )
                bot.register_next_step_handler(msg, distance_from_centre)
            else:
                end_conversation(user_id=str(call.from_user.id), chat_id=call.message.chat.id)

        else:
            bot.send_message(chat_id=call.message.chat.id, text=interface['errors']['date2'][language])
            db.get_settings(user_id=call.from_user.id, key='date1', remove_kebab=True)
            db.get_settings(user_id=call.from_user.id, key='date2', remove_kebab=True)
            choose_date(call)


def distance_from_centre(message: types.Message) -> None:
    """
    Функция получающая дистанцию от центра в километрах
    :param message:  Message
    :return: None
    """

    logger.info(f'Function {distance_from_centre.__name__} called, user input is in condition. use arg: '
                f'distance =  {message.text}')
    if message.text.strip().isdigit():
        db.set_settings(
            user_id=str(message.from_user.id),
            key='distance',
            value=message.text.strip()
        )
        reply = menu.price_reply(
            language=db.get_settings(message.from_user.id, key='language'),
            currency=db.get_settings(message.from_user.id, key='currency')
        )
        msg = bot.send_message(message.chat.id, reply)
        bot.register_next_step_handler(msg, min_max_price)
    else:
        logger.info(f'Function {distance_from_centre.__name__} called, user input IS NOT in  condition.')
        msg = bot.send_message(
            message.chat.id,
            interface['questions']['radius'][db.get_settings(message.from_user.id, key='language')]
        )
        bot.register_next_step_handler(msg, distance_from_centre)


def min_max_price(message: types.Message) -> None:
    """
    Фнкция обрабатывающая пользовательский ввод максимальной и минимальной цены
    :param message:  Message
    :return: None
    """
    logger.info(f'Function {min_max_price.__name__} called, user input is in condition. use arg: '
                f'distance =  {message.text} user_id {message.from_user.id}')
    if message.text.replace(' ', '').isdigit() and len(message.text.split()) == 2:
        min_price, max_price = sorted(message.text.strip().split(), key=int)
        logger.info(f'min pr {min_price}, max pr {max_price}')
        db.set_settings(
            user_id=str(message.from_user.id),
            key='min_price',
            value=min_price
        )
        db.set_settings(
            user_id=str(message.from_user.id),
            key='max_price',
            value=max_price
        )

        end_conversation(user_id=str(message.from_user.id), chat_id=message.chat.id)
    else:
        logger.info(f'Function {min_max_price.__name__} called, user input IS NOT in  condition.')
        msg = bot.send_message(
            message.chat.id,
            interface['errors']['price'][db.get_settings(message.from_user.id, key='language')])
        bot.register_next_step_handler(msg, min_max_price)


def end_conversation(user_id: str, chat_id: int) -> None:
    """
    конец диалога, формирование ответов
    :param user_id: id пользователя
    :param chat_id: id чата
    :return: None
    """
    lang = db.get_settings(user_id=user_id, key='language')
    msg = bot.send_message(chat_id=chat_id, text='опять мясной мешок заставляет работать')
    bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=interface['responses']['loading'][lang])
    hotels = hotels_finder.get_hotels(user_id=user_id)
    bot.delete_message(chat_id=chat_id, message_id=msg.message_id)

    logger.info(f'Function {end_conversation.__name__} starts with : {hotels}')

    if not hotels or len(hotels.keys()) < 1:
        bot.send_message(chat_id, interface['errors']['hotels'][lang])
    elif 'bad_request' in hotels:
        bot.send_message(chat_id, interface['errors']['bad_request'][lang])
    else:
        bot.send_message(
            chat_id,
            interface['responses']['hotels_found'][lang] + ' ' + str(len(hotels.keys()))
        )
        for hotel_id, hotel_info in hotels.items():
            list_of_urls = hotel_info['photo']
            message = hotel_info['message']
            if len(list_of_urls) < 1:
                bot.send_message(chat_id, message, parse_mode='HTML')
            else:
                media_group = [types.InputMediaPhoto(media=i_elem) for i_elem in list_of_urls]
                bot.send_media_group(chat_id, media=media_group)
                bot.send_message(chat_id, message, parse_mode='HTML')
    bot.send_message(chat_id=chat_id, text=interface['questions']['save'][lang], reply_markup=kb.history_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('save'))
def saving_buttons_catcher(call):
    """
    Обработчик нажатых кнопок меню выбора сохранения истории запроса
    :param call: Callback
    :return: None
    """
    logger.info(f'function {saving_buttons_catcher.__name__} was called')
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data.endswith('yes'):
        db.set_history(call.from_user.id)
    main_menu(user_id=call.from_user.id, chat_id=call.message.chat.id, command='another_one')


try:
    bot.infinity_polling()
except Exception as err:
    logger.opt(exception=True).error(f'Unexpected error: {err}')
