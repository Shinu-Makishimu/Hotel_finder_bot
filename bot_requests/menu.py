from language import interface
from loguru import logger


def start_reply(first_name:str, last_name:str, status:str, language:str) ->str:
    """
    обработчик команды старт
    :param message:
    :return:
    """
    logger.info(f'"{start_reply.__name__}" command is called')
    person = f' {first_name} {last_name}!\n'
    reply = interface['responses']['greeting_1'][language] + person
    if status == 'new':
        reply += interface['responses']['greeting_new'][language]
    else:
        reply += interface['responses']['greeting_old'][language]
    return reply


def settings_reply(language:str, currency:str):
    reply = "{menu}\n{ans}\n {your_lang} {lang}\n {your_cur} {cur}".format(
        menu=interface['elements']['settings_menu'][language],
        ans=interface['responses']['your_settings'][language],
        your_lang=interface['responses']['current_language'][language],
        lang=language,
        your_cur=interface['responses']['current_currency'][language],
        cur=currency
    )
    return reply

