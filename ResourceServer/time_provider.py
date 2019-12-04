from datetime import datetime
from time import time


class TimeProvider:
    @staticmethod
    def current_time():
        return str(datetime.now())

    @staticmethod
    def epoch_time():
        return int(time())
