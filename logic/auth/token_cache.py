import time

class TokenCache:
    """Class that provides a generic interface to a token cache.

    Currently this uses a static object but it  could, for example, later be
    replaced by a redis backend while the interface (the functions) remains the
    same
    """

    __DICT_CACHE = {}

    def add_token(self, email, token):
        timestamp = str(int(time.time() * 1000))
        TokenCache.__DICT_CACHE[email + timestamp] = token

    def verify_token(self, email):
        for k in TokenCache.__DICT_CACHE.keys():
            if email in k:
                return True
        return False

    def delete_tokens_for_user(self, email):
        keys = [k for k in TokenCache.__DICT_CACHE.keys()]
        for k in keys:
            if email in k:
                TokenCache.__DICT_CACHE.pop(k)

    def delete_all_tokens(self):
        TokenCache.__DICT_CACHE.clear()