from loguru import logger
from language import interface
from accessory import get_date


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

def history_reply(record: tuple, lang:str)-> str:
    search_type = record[2]
    search_date = get_date(int(record[5]))
    city = record[4]
    currency = record[13]
    hotel_count= record[6]
    photo_count = record[7]
    check_in = get_date(int(record[11]))
    check_out= get_date(int(record[12]))
    message = f"\n{interface['elements']['date_search'][lang]}: {search_date}\n" \
              f"{interface['responses']['current_currency'][lang]}: {currency}\n" \
              f"{interface['elements']['city'][lang]}: {city}\n" \
              f"{interface['elements']['hotels_in_res'][lang]}: {hotel_count}\n" \
              f"{interface['elements']['photos_in_res'][lang]}: {photo_count}\n" \
              f"{interface['responses']['check_in'][lang]}: {check_in}\n" \
              f"{interface['responses']['check_out'][lang]}: {check_out}\n"
    if search_type == 'bestdeal':
        r = record[8]
        min_price= record[9]
        max_price= record [10]
        message +=f"{interface['elements']['radius'][lang]}: {r}\n" \
        f"{interface['elements']['price_min'][lang]}: {min_price}\n" \
        f"{interface['elements']['price_max'][lang]}: {max_price}\n" \

    return message
