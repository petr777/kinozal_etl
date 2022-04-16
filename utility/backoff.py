from functools import wraps
from time import sleep
from loguru import logger


def backoff(
        start_sleep_time=0.1,
        factor=2,
        border_sleep_time=10,
        logger=logger,
):
    """
    Функция для повторного выполнения функции через некоторое время,
    если возникла ошибка. Использует наивный экспоненциальный рост времени
    повтора (factor) до граничного времени ожидания (border_sleep_time)
    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            n = 0
            while True:
                sleep_time = start_sleep_time * factor ** n
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    logger.error(
                        f'Функции не выполненна "{func.__name__}" ошибка {err}'
                    )
                    if sleep_time >= border_sleep_time:
                        sleep_time = border_sleep_time
                    else:
                        n += 1
                    logger.info(f'reconnect again after {sleep_time} seconds')
                    sleep(sleep_time)


        return inner

    return func_wrapper