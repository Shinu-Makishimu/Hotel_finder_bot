# from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
# # библиотека телеграмбот не подключена
#
# @bot.message_handler(commands=['calendar'])
# def start(message):
#     """
#     простой календарик из модуля календарь
#     :param message:
#     :return:
#     """
#     calendar, step = DetailedTelegramCalendar().build()
#     bot.send_message(message.chat.id,
#                      f"Select {LSTEP[step]}",
#                      reply_markup=calendar)
#
#
# @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
# def cal(calendar):
#     result, key, step = DetailedTelegramCalendar().process(calendar.data)
#     if not result and key:
#         bot.edit_message_text(f"Select {LSTEP[step]}",
#                               calendar.message.chat.id,
#                               calendar.message.message_id,
#                               reply_markup=key)
#     elif result:
#         bot.edit_message_text(f"You selected {result}",
#                               calendar.message.chat.id,
#                               calendar.message.message_id)
#
#



# def send_action(action): # декоратор который соообщает о действиях бота
#     def decorator(func):
#         @functools.wraps(func)
#         def command_func(message, *args, **kwargs):
#             bot.send_chat_action(chat_id=message.chat.id, action=action)
#             return func(message, *args, **kwargs)
#         return command_func
#     return decorator