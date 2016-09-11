from contextlib import ContextDecorator
from redis import StrictRedis

from utils.config import config


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
