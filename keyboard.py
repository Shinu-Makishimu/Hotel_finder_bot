import telebot

settings_keyboard = telebot.types.InlineKeyboardMarkup()
settings_keyboard.add(
    telebot.types.InlineKeyboardButton(text='money', callback_data='set_money'),
    telebot.types.InlineKeyboardButton(text='language', callback_data='set_language'),
    telebot.types.InlineKeyboardButton(text='back', callback_data='set_back')
)

main_menu_keyboard = telebot.types.InlineKeyboardMarkup()
main_menu_keyboard.add(
    telebot.types.InlineKeyboardButton(text='Low price', callback_data='main_lowprice'),
    telebot.types.InlineKeyboardButton(text='Best deal', callback_data='main_bestdeal'),
    telebot.types.InlineKeyboardButton(text='High price', callback_data='main_highprice'),
    telebot.types.InlineKeyboardButton(text='My history', callback_data='main_history'),
    telebot.types.InlineKeyboardButton(text='Settings', callback_data='main_settings'),
    telebot.types.InlineKeyboardButton(text='Help', callback_data='main_help')
)

money_keyboard = telebot.types.InlineKeyboardMarkup()
money_keyboard.add(
    telebot.types.InlineKeyboardButton(text='рубли', callback_data='money_RUB'),
    telebot.types.InlineKeyboardButton(text='dollars', callback_data='money_USD'),
    telebot.types.InlineKeyboardButton(text='euro', callback_data='money_EUR'),
    # telebot.types.InlineKeyboardButton(text='cancel', callback_data='money_cancel')
)

language_keyboard = telebot.types.InlineKeyboardMarkup()
language_keyboard.add(
    # telebot.types.InlineKeyboardButton(text='cancel', callback_data='language_cancel'),
    # telebot.types.InlineKeyboardButton(text='Spain', callback_data='language_ESPA'),
    telebot.types.InlineKeyboardButton(text='English', callback_data='language_en_US'),
    telebot.types.InlineKeyboardButton(text='Русский', callback_data='language_ru_RU')
)

photo_keyboard = telebot.types.InlineKeyboardMarkup()
photo_keyboard.add(
    telebot.types.InlineKeyboardButton(text='NO', callback_data='photo_no'),
    telebot.types.InlineKeyboardButton(text='YES', callback_data='photo_yes'),
)

history_keyboard = telebot.types.InlineKeyboardMarkup()
history_keyboard.add(
    telebot.types.InlineKeyboardButton(text='NO', callback_data='save_no'),
    telebot.types.InlineKeyboardButton(text='YES', callback_data='save_yes'),
)

help_keyboard = telebot.types.InlineKeyboardMarkup()
help_keyboard.add(
    telebot.types.InlineKeyboardButton(text='/lowprice', callback_data='help_low'),
    telebot.types.InlineKeyboardButton(text='/bestdeal', callback_data='help_best'),
    telebot.types.InlineKeyboardButton(text='/highprice', callback_data='help_high'),
    telebot.types.InlineKeyboardButton(text='/settings', callback_data='help_sett'),
    telebot.types.InlineKeyboardButton(text='Back', callback_data='help_back')
)
