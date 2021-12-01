import sqlite3
import functools
import keyboard as kb
from telebot import TeleBot
from settings import commands, buttons_eng, API_TOKEN, User

bot = TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    client = User.get_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
    chat_id = message.chat.id
    text = f"Hi! {client.name} {client.surname}!\n {buttons_eng['greet']} {client.id})"
    bot.send_message(chat_id, text)
    main_choice(message)


@bot.message_handler(commands=['help'])
def help_message(message):
    chat_id = message.chat.id
    help_text = buttons_eng['help']
    for command, description in commands.items():
        help_text += f"/{command}: {description}\n"
    bot.send_message(chat_id, help_text)


@bot.message_handler(commands=['main'])
def main_choice(message):
    text_message = buttons_eng['main_h']
    bot.send_message(message.from_user.id, text_message, reply_markup=kb.main_kb)


@bot.callback_query_handler(func=lambda call: True)
def callback_main_menu(call):
    if call.message and call.data in buttons_eng.keys():
        bot.send_message(call.message.chat.id, f"Your choice is {buttons_eng[call.data]}")


bot.infinity_polling()
