import sqlite3
import functools
import os
import keyboard as kb
from telebot import TeleBot
from settings import commands, buttons_eng, API_TOKEN, content_type_ANY
from database import add_user_to_db, User, work_with_keys, return_all_req

bot = TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    """
    обработчик команды старт.
    1. собираю в переменную данные о пользователе.
    на его основе создаю экземпляр класса User, ставлю флаг активной сессии.
    формирую приветствие и отправляю сообщение. сразу вызываю main_choice
    :param message:
    :return:
    """
    user_data = [message.from_user.id,
                 message.from_user.first_name,
                 message.from_user.last_name,
                 message.from_user.username]
    print('юзер дата из start', user_data)
    client = User.get_user(user_data)  # создаем экземпляр для работы
    print(client)
    client.is_running = True  # ставим метку активной сессии
    chat_id = message.chat.id
    text = f"Hi! {client.name} {client.surname}!\n {buttons_eng['greet']} {client.id}\n)"
    bot.send_message(chat_id, text)
    main_choice(message)


@bot.message_handler(commands=['help'])  # хелп
def help_message(message):
    """
    Обработчик команды хелп
    :param message:
    :return:
    """
    chat_id = message.chat.id
    help_text = buttons_eng['help']
    for command, description in commands.items():
        help_text += f"/{command}: {description}\n"
    bot.send_message(chat_id, help_text)


@bot.message_handler(commands=['main'])
def main_choice(message):
    """
    главное меню с кнопками. клавиатура и кнопки берутся из файла keyboard.
    отправляю сообщение с инлайн кнопками
    :param message:
    :return:
    """
    text_message = buttons_eng['main_h']
    bot.send_message(message.from_user.id, text_message, reply_markup=kb.main_kb)


@bot.message_handler(content_types=['text'])  # ответчик на текст
def text_handler(message):
    """
    Ответчик на текстовое сообщение, добавлено в тестовых целях
    :param message:
    :return:
    """
    text = message.text.lower()
    chat_id = message.chat.id
    date = message.date
    response = 'я о тебе знаю:\n дата сообщения {date},\n твой id {id},' \
               '\n имя {name}, второе имя{last_name}, ник {username} '.format(
        date=date,
        id=message.from_user.id,
        name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username
    )
    if text == '??':
        bot.send_message(chat_id, response)
    else:
        bot.send_message(chat_id, "i don't understand")


@bot.message_handler(content_types=[content_type_ANY])  # ответчик на ANY
def text_handler(message):
    """
    Ответчик если пользователь послал: документ, войс, пикчу, видео, аудио.
    в переменной хранится лист, создается в файле сеттингс
    :param message:
    :return:
    """
    chat_id = message.chat.id
    bot.send_message(chat_id, 'incorrect data')


#################################################
# ответчики


@bot.callback_query_handler(func=lambda call: call.data in ['low', 'high'])  # ветка прайс лоу и хай
def callback_main_menu(call):
    """
    Ответчик на пункт меню low и high.
    снова создаю переменную с юзер дата для того что бы с помощью
    функции work_with_keys записываю в экземпляр то что выбрал пользователь, что бы
    формировать его историю запроса.
    (метод наиболее дегенеративный, переписать!)
    в переменную текст формирую ответ, отправляю пользователю, исполняю следующий шаг
    :param call:
    :return:
    """
    user_data = [call.from_user.id,
                 call.from_user.first_name,
                 call.from_user.last_name,
                 call.from_user.username]
    key = call.data
    chat_id = call.message.chat.id
    text = f"Exellent! Your choice is {key} price hotel!\nNow, send me country name"
    work_with_keys(user_data, key)
    bot.send_message(chat_id, text)
    bot.register_next_step_handler(call.message, choise_city)


def choise_city(message):
    """
    снова создаю переменню с данными пользователя что бы добавить в список
    историю запроса
    выполняется простенькая проверка на наличие недопустимых символов(цифр) в тексте.
    как вариант переделать на регулярку, что бы в тексте были только буквы без символов
    с помощью функции  work_with_keys записываю то что ввел пользователь

    :param message:
    :return:
    """
    user_data = [message.from_user.id,
                 message.from_user.first_name,
                 message.from_user.last_name,
                 message.from_user.username]

    chat_id = message.chat.id
    text = message.text
    if not text.isalpha():
        message = bot.send_message(chat_id, 'country name has incorrect symbols')
        bot.register_next_step_handler(message, choise_city)  # askSource
        return
    work_with_keys(user_data, text)
    message = bot.send_message(chat_id, 'your input is ' + text + ' Now, enter the city')
    bot.register_next_step_handler(message, low_price_city)


def low_price_city(message):
    """
    почти всё тоже самое что и в предыдущем шаге, только с помощью функции return_all_req
    смотрю что ввел пользователь.
    :param message:
    :return:
    """
    user_data = [message.from_user.id,
                 message.from_user.first_name,
                 message.from_user.last_name,
                 message.from_user.username]

    chat_id = message.chat.id
    text = message.text
    if not text.isalpha():
        message = bot.send_message(chat_id, 'city name has incorrect symbols')
        bot.register_next_step_handler(message, low_price_city)
        return
    work_with_keys(user_data, text)
    rspomce = return_all_req(user_data)
    bot.send_message(chat_id, f'here is some result {rspomce}. FIN')


bot.infinity_polling()
