from redis import StrictRedis

from helpers.config import config


def _init_redis():
    host = config.get('app', 'host')
    port = config.get('redis', 'port')
    db = config.get('redis', 'db')

    return StrictRedis(host=host, port=port, db=db)

redis = _init_redis()
