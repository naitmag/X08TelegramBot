import logging
import os
from datetime import datetime
from logging import handlers
import pytz


def converter(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    tzinfo = pytz.timezone('Europe/Moscow')
    return tzinfo.localize(dt)


class Formatter(logging.Formatter):
    """override logging.Formatter to use an aware datetime object"""

    def formatTime(self, record, datefmt=None):
        dt = converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s


logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.handlers.RotatingFileHandler(
    filename=os.path.join(os.path.dirname(__file__), 'logs', 'feedback.log'),
    mode='a', maxBytes=1024 * 100, backupCount=3)

file_handler.setFormatter(Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'), )
logger.addHandler(file_handler)
