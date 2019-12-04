from time import time


class AuthCodesDatabase:
    AUTH_CODE_EXPIRATION_TIME_SEC = 60
    CLEANUP_THRESHOLD = 10000

    def __init__(self):
        self.codes = dict()

    def add(self, auth_code, scope):
        self.codes[auth_code] = (time(), scope)

    def is_valid(self, auth_code):
        if auth_code not in self.codes:
            return False
        creation_time, _ = self.codes[auth_code]
        return time() < creation_time + AuthCodesDatabase.AUTH_CODE_EXPIRATION_TIME_SEC

    def get_scope(self, auth_code):
        _, scope = self.codes[auth_code]
        return scope

    def remove(self, auth_code):
        del self.codes[auth_code]
        if len(self.codes) > AuthCodesDatabase.CLEANUP_THRESHOLD:
            self.cleanup()

    def cleanup(self):
        expired_auth_codes = [auth_code for auth_code, data
                              in self.codes.items()
                              if data[0] + AuthCodesDatabase.AUTH_CODE_EXPIRATION_TIME_SEC < time()]
        for auth_code in expired_auth_codes:
            del self.codes[auth_code]
