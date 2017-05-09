import time

from contextlib import ContextDecorator
from redis import StrictRedis, exceptions

from utils.config import config
from redis_db import RedisTransactionException


def _init_redis():
    host = config.get('redis', 'host')
    port = config.get('redis', 'port')
    db = config.get('redis', 'db')

    return StrictRedis(host=host, port=port, db=db)

redis = _init_redis()


class redis_session(ContextDecorator):
    def __enter__(self):
        self.pipeline = redis.pipeline()
        return self.pipeline

    def __exit__(self, *args):
        self.pipeline.execute()
        return False


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


def redis_watch(pipe, id=None, *args):
    fields = args
    pipe.watch(*[f.key(id) for f in fields])
