from cmath import log
from typing import Callable, Any, List, Dict, Optional
from time import sleep
import logging

from prawcore import exceptions


def get_logger() -> logging.Logger:
    logger = logging.getLogger('RDS-PROJECT')
    fhandler = logging.FileHandler(filename='logs.log', mode='a')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fhandler.setFormatter(formatter)
    logger.addHandler(fhandler)
    logger.setLevel(logging.DEBUG)
    return logger


def safe_call(
    func: Callable, 
    args: Optional[List] = None,
    kwargs: Optional[Dict] = None,
    max_retries: int = 3,
    sleep_time: int = 1,
) -> Any:
    """
    Wraps a function and retries it if it raises a NotFound exception (404).
    """
    logger = get_logger()

    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    while max_retries > 0:
        try:
            return func(*args, **kwargs)
        except exceptions.NotFound as e:
            logger.info(e)
            sleep(sleep_time)
            max_retries -= 1
    
    logger.error(f"Failed to execute function {func.__name__}\n{e}")
    raise e