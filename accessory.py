import re
import datetime
from loguru import logger

def check_message(message):

    status = get_navigate(message)
    text = message.text.strip()

    if status == 'lowprice':
        return True
    elif status == 'highprice' :
        return True
    elif status == 'bestdeal':
        return True
    else:
        return False


def hotel_price(hotel: dict) -> int:
    """
    return hotel price
    :param hotel: dict - hotel information
    :return: integer or float like number
    """

    price = 0

    if hotel.get('ratePlan').get('price').get('exactCurrent'):
        price = hotel.get('ratePlan').get('price').get('exactCurrent')
    else:
        price = hotel.get('ratePlan').get('price').get('current')
        price = int(re.sub(r'[^0-9]', '', price))


    return price


def address(hotel, message):
    """
    returns hotel address
    :param msg: Message
    :param hotel: dict - hotel information
    :return: hotel address
    """
    message = ('no_information', message)
    logger.info(f'Function {address.__name__} called with argument: hotel {hotel}')

    if hotel.get('address'):
        result = hotel.get('address').get('streetAddress', message)
    return message


def rating(rating, message):
    """
    returns rating hotel in asterisks view
    :param rating: hotel rating
    :param msg: Message
    :return: string like asterisks view hotel rating
    """
    if not rating:
        return ('no_information', message)
    return '⭐' * int(rating)


def get_timestamp(y,m,d):
    logger.info(f'Function {get_timestamp.__name__} called with argument:year {y} month{m} day{d}')
    return datetime.datetime.timestamp(datetime.datetime(y,m,d))


def get_date(tmstmp):
    logger.info(f'Function {get_date.__name__} called with argument: {tmstmp}')

    return datetime.datetime.fromtimestamp(tmstmp).date()


def check_dates(check_in, check_out):
    if float(check_in) >= float(check_out):
        return False
    else:
        return True