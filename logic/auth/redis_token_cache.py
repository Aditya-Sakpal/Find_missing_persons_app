from external_services.redis.connection import get_redis_connection_pool
from logic.auth.token_cache import TokenCache
from redis import StrictRedis
from datetime import datetime
import config


class RedisTokenCache(TokenCache):

    def __init__(self):
        self.client = StrictRedis(connection_pool=get_redis_connection_pool())

    def add_token(self, key, token):

        redis_token_key = key
        self.client.hset(
            name=config.redis_hset_name,
            key=redis_token_key,
            value=token
        )

        return True

    def verify_token(self, key):
        if not self.client.hexists(name=config.redis_hset_name, key=key):
            return False
        return True

    def delete_tokens_for_user(self, key):
        self.client.hdel(config.redis_hset_name, key)

    def delete_all_tokens(self):
        for key in self.client.hkeys(config.redis_hset_name):
            self.client.hdel(config.redis_hset_name, key)
