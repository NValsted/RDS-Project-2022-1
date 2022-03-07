from typing import Callable, Any, List, Dict, Optional
from time import sleep
import logging
import traceback

from prawcore import exceptions


def get_logger(name: str = "RDS-PROJECT") -> logging.Logger:
    logger = logging.getLogger(name)
    fhandler = logging.FileHandler(filename="logs.log", mode="a")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
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
    exception: Exception = exceptions.NotFound,
    raise_on_failure: bool = True,
) -> Any:
    """
    Wraps a function and retries it if it raises an exception.
    """
    logger = get_logger()

    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    error = Exception("Unknown error")

    while max_retries > 0:
        try:
            return func(*args, **kwargs)
        except exception as e:
            error = e
            max_retries -= 1
            logger.info(
                f"{func.__name__} failed with args {args} and kwargs {kwargs}\n"
                f"{e}\n{traceback.format_exc()}"
                f"{max_retries} retries left"
            )
            sleep(sleep_time)

    if raise_on_failure:
        logger.error(f"Failed to execute function {func.__name__}")
        raise error
