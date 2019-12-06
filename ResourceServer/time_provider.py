from time import time
from datetime import datetime


class TimeProvider:
    @staticmethod
    def current_time():
        return str(datetime.now())

    @staticmethod
    def epoch_time():
        return int(time())
