import datetime

from loguru import logger


def get_timestamp(date: datetime)-> float:
    """
    функция конвертации даты в таймстап для удобного хранения в бд
    :param date:
    :return:
    """
    y, m, d = [int(i) for i in str(date).split('-')]
    logger.info(f'Function {get_timestamp.__name__} called with argument:year {y} month{m} day{d}')
    return datetime.datetime.timestamp(datetime.datetime(y,m,d))


def get_date(tmstmp: float)-> datetime:
    """
    конвертация формата таймстамп в дату
    :param tmstmp:
    :return:
    """
    logger.info(f'Function {get_date.__name__} called with argument: {tmstmp}')

    return datetime.datetime.fromtimestamp(int(tmstmp[:-2])).date().strftime("%Y-%m-%d")


def check_dates(check_in: float, check_out:float) -> bool:
    """
    проверка. если чекин больше чекаута возвращается false
    :param check_in:
    :param check_out:
    :return:
    """
    if check_in >= check_out:
        return False
    else:
        return True


def create_html_links(l:list) ->str:
    pass