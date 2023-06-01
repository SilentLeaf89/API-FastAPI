import logging
from functools import lru_cache

from core.logger import LOGGING


@lru_cache()
def get_logger():
    logging.config.dictConfig(LOGGING)
    return logging.getLogger()
