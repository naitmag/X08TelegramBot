import logging
import os
from datetime import datetime
from logging import handlers
import pytz


class Formatter(logging.Formatter):
    """override logging.Formatter to use an aware datetime object"""

    @staticmethod
    def converter(timestamp):
        return datetime.now(tz=pytz.timezone("Europe/Minsk"))

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
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

formatter = Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
