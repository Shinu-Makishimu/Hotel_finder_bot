import sqlite3
import functools
import keyboard as kb
from telebot import TeleBot
from settings import commands, buttons_eng, API_TOKEN, User, content_type_ANY

bot = TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    """
    обработчик команды старт
    :param message:
    :return:
    """
    client = User.get_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
    chat_id = message.chat.id
    text = f"Hi! {client.name} {client.surname}!\n {buttons_eng['greet']} {client.id})"
    bot.send_message(chat_id, text)
    main_choice(message)


@bot.message_handler(commands=['help'])# хелп
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
    главное меню с кнопками. клавиатура и кнопки берутся из файла keyboard
    :param message:
    :return:
    """
    text_message = buttons_eng['main_h']
    bot.send_message(message.from_user.id, text_message, reply_markup=kb.main_kb)


@bot.message_handler(content_types=['text']) #ответчик на текст
def text_handler(message):
    """
    Ответчик на текстовое сообщение
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


@bot.message_handler(content_types=[content_type_ANY]) #ответчик на ANY
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


@bot.callback_query_handler(func=lambda call: call.data == 'low') #ветка лоу прайс
def callback_main_menu(call):
    """
    Ответчик на пункт меню low
    :param call:
    :return:
    """
    chat_id = call.message.chat.id
    text = "Exellent! Your choice is low price hotel!\nNow, send me country name"
    # text2 = call.message
    bot.send_message(chat_id, text)
    bot.register_next_step_handler(call.message, low_price_cntr)


def low_price_cntr(message):
    chat_id = message.chat.id
    text = message.text
    if not text.isalpha():
        message = bot.send_message(chat_id, 'country name has incorrect symbols')
        bot.register_next_step_handler(message, low_price_cntr) #askSource
        return
    message = bot.send_message(chat_id, 'your input is ' + text + ' Now, enter the city')
    bot.register_next_step_handler(message, low_price_city)

def low_price_city(message):
    chat_id = message.chat.id
    text = message.text
    if not text.isalpha():
        message = bot.send_message(chat_id, 'city name has incorrect symbols')
        bot.register_next_step_handler(message, low_price_city)
        return
    bot.send_message(chat_id, 'here is some result from api. FIN')












bot.infinity_polling()
