import re

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