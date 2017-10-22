import time

from redis import StrictRedis, exceptions

from utils.config import config
from redis_db import RedisTransactionException


def _init_redis(db):
    host = config.get('redis', 'host')
    port = config.get('redis', 'port')

    return StrictRedis(host=host, port=port, db=db)


redis = _init_redis(config.get('redis', 'db'))


DEFAULT_TRANSACTION_TIMEOUT = 5


def redis_retry_transaction(timeout=DEFAULT_TRANSACTION_TIMEOUT):
    def _redis_retry_transaction(fn):
        def decorator(pipe, *args, **kwargs):
            end = time.time() + timeout
            while time.time() < end:
                try:
                    return fn(pipe, *args, **kwargs)
                except exceptions.WatchError:
                    pass

            raise RedisTransactionException()
        return decorator
    return _redis_retry_transaction
