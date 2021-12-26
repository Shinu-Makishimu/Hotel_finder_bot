from language import interface
from loguru import logger


def start_reply(first_name: str, last_name: str, status: str, language: str) -> str:
    """
    формирует строку приветсятвия
    :param first_name:
    :param last_name:
    :param status:
    :param language:
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


def settings_reply(language: str, currency: str) -> str:
    """
    формирует строку текущих настроек
    :param language:
    :param currency:
    :return:
    """
    reply = "\t\t{menu}\n\n{ans}:\n\t{your_lang}:\t{lang}\n\t{your_cur}:\t{cur}".format(
        menu=interface['elements']['settings_menu'][language],
        ans=interface['responses']['your_settings'][language],
        your_lang=interface['responses']['current_language'][language],
        lang=language[3:],
        your_cur=interface['responses']['current_currency'][language],
        cur=currency
    )
    return reply


def price_reply(language:str, currency: str) -> str:
    reply = "{menu}\n{ans}: {cur}".format(
        menu=interface['questions']['price'][language],
        ans=interface['responses']['current_currency'][language],
        cur=currency
    )
    return reply
