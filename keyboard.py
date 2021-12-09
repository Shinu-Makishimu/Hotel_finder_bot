import telebot

button_country = telebot.types.InlineKeyboardButton(text='country', callback_data='set_country')
button_money = telebot.types.InlineKeyboardButton(text='money', callback_data='set_money')
button_language = telebot.types.InlineKeyboardButton(text='language', callback_data='set_language')
button_back = telebot.types.InlineKeyboardButton(text='back', callback_data='set_back')
settings_keyboard = telebot.types.InlineKeyboardMarkup().add(
    button_country,
    button_money,
    button_language,
    button_back
    )

button_lowprice = telebot.types.InlineKeyboardButton(text='Low price', callback_data='lowprice')
button_bestdeal = telebot.types.InlineKeyboardButton(text='Best deal', callback_data='main_high')
button_highprice = telebot.types.InlineKeyboardButton(text='High price', callback_data='main_high')
button_history = telebot.types.InlineKeyboardButton(text='My history', callback_data='main_hist')
button_settings = telebot.types.InlineKeyboardButton(text='Settings', callback_data='main_settings')

main_menu_keyboard = telebot.types.InlineKeyboardMarkup().add(
    button_lowprice,
    button_bestdeal,
    button_highprice,
    button_history,
    button_settings
    )

button_m_rus = telebot.types.InlineKeyboardButton(text='рубли', callback_data='money_RUB')
button_m_eng = telebot.types.InlineKeyboardButton(text='dollars', callback_data='money_USD')
button_m_spain = telebot.types.InlineKeyboardButton(text='euro', callback_data='money_EUR')
button_m_cancer = telebot.types.InlineKeyboardButton(text='cancel', callback_data='cancel')
money_keyboard = telebot.types.InlineKeyboardMarkup().add(
    button_m_rus,
    button_m_eng,
    button_m_spain
    )

button_l_rus = telebot.types.InlineKeyboardButton(text='Русский', callback_data='language_RUSS')
button_l_eng = telebot.types.InlineKeyboardButton(text='English', callback_data='language_ENGL')
button_l_spain = telebot.types.InlineKeyboardButton(text='Spain', callback_data='language_ESPA')
button_l_cancer = telebot.types.InlineKeyboardButton(text='cancel', callback_data='cancel')
language_keyboard = telebot.types.InlineKeyboardMarkup().add(
    button_l_rus,
    button_l_eng,
    button_l_spain
    )
