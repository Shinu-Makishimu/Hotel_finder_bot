import datetime
from typing import Any
from loguru import logger


def get_timestamp(date: datetime)-> int:
    """
    функция конвертации даты в таймстап для удобного хранения в бд
    :param date:
    :return:
    """
    y, m, d = [int(i) for i in str(date).split('-')]
    logger.info(f'Function {get_timestamp.__name__} called with argument:year {y} month{m} day{d}')
    result = int(datetime.datetime.timestamp(datetime.datetime(y, m, d)))
    logger.info(f'Function {get_timestamp.__name__} create result: {result}')

    return result


def get_date(tmstmp: int, days: bool = False) -> datetime:
    """
    конвертация формата таймстамп в дату
    :param days:
    :param tmstmp:
    :return:
    """

    logger.info(f'Function {get_date.__name__} called with argument: {tmstmp}')
    try:
        if days:
            result = datetime.datetime.fromtimestamp(tmstmp)
        else:
            result = datetime.datetime.fromtimestamp(tmstmp).date().strftime("%Y-%m-%d")
        logger.info(f'Function {get_date.__name__} create result: {result}')
    except Exception as error:
        logger.error(f'function crushed with {error}')

    return result


def check_dates(check_in: int, check_out:int) -> bool:
    """
    проверка. если чекин больше чекаута возвращается false
    :param check_in:
    :param check_out:
    :return:
    """
    logger.info(f'Function {check_dates.__name__} called with argument: {check_in} {check_out}')
    if check_in >= check_out:
        return False
    else:
        return True


