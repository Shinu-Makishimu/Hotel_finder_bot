import sqlite3
import functools
from telebot import TeleBot, types
from settings import commands, API_TOKEN, User

bot = TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    client = User.get_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
    chat_id = message.chat.id
    text = f'{client.name} {client.surname}!\n' \
           f'This is a low-quality bot from a dumb developer.' \
           f'\n(btw, your id is {client.id})'
    bot.send_message(chat_id, text)
    main_choice(message)


@bot.message_handler(commands=['help'])
def help_message(message):
    chat_id = message.chat.id
    help_text = 'Following commands are avaliable: \n'
    for command, description in commands.items():
        help_text += f"/{command}: {description}\n"
    bot.send_message(chat_id, help_text)


@bot.message_handler(commands=['main'])
def main_choice(message):
    low_pr = types.InlineKeyboardButton('Low price', callback_data='low')
    best_dl = types.InlineKeyboardButton('Best deal', callback_data='best')
    high_pr = types.InlineKeyboardButton('High price', callback_data='high')
    history = types.InlineKeyboardButton('history', callback_data='hist')
    text_message = 'Click on the button with the desired operation'
    keyboard = types.InlineKeyboardMarkup().row(low_pr, best_dl, high_pr, history)
    bot.send_message(message.from_user.id, text_message, reply_markup=keyboard)


@bot.message_handler(func=lambda call: call == 'low')
def low_price(message):
    bot.send_message(message.from_user.id, 'You has benn pushed on button lowprice')


bot.infinity_polling()
