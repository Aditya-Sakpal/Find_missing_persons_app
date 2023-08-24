import redis
import config

redis_pool = None


def get_redis_connection_pool():
    global redis_pool

    if redis_pool is None:
        if "localhost" in config.redis_url:
            redis_pool = redis.ConnectionPool(
                host=config.redis_host,
                port=config.redis_port,
                password=config.redis_password,
                connection_class=redis.SSLConnection,
                db=0)
        else:
            # redis_pool = redis.ConnectionPool(
            #     host=config.redis_host,
            #     port=config.redis_port,
            #     password=config.redis_password,
            #     db=0)
            config.default_log.info("NOTE: Using insecure redis connection")
            redis_pool = redis.ConnectionPool(
                host=config.redis_host,
                port=config.redis_port,
                password=config.redis_password,
                db=0)

    return redis_pool