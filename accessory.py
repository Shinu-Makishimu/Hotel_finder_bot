import datetime

from loguru import logger


def get_timestamp(date: datetime)-> float:
    """

    :rtype: object
    """
    y, m, d = [int(i) for i in str(date).split('-')]
    logger.info(f'Function {get_timestamp.__name__} called with argument:year {y} month{m} day{d}')
    return datetime.datetime.timestamp(datetime.datetime(y,m,d))


def get_date(tmstmp: float)-> datetime:
    logger.info(f'Function {get_date.__name__} called with argument: {tmstmp}')

    return datetime.datetime.fromtimestamp(int(tmstmp[:-2])).date().strftime("%Y-%m-%d")


def check_dates(check_in: float, check_out:float) -> bool:
    if check_in >= check_out:
        return False
    else:
        return True
