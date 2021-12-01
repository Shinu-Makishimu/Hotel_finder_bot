from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove

low_pr = InlineKeyboardButton('Low price', callback_data='low')
best_dl = InlineKeyboardButton('Best deal', callback_data='best')
high_pr = InlineKeyboardButton('High price', callback_data='high')
history = InlineKeyboardButton('history', callback_data='hist')
main_kb = InlineKeyboardMarkup().row(low_pr, best_dl, high_pr, history)
