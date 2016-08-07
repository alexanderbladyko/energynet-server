from utils.redis import redis
from helpers.redis import get_hashset


class Game:
    def __init__(self, data):
        self.data = data

    @classmethod
    def get_new_id(cls):
        return redis.incr('game:index')

    @classmethod
    def get_all(cls):
        ids = redis.lrange('games', 0, -1)
        return [
            get_hashset(redis, 'game:%s' % id.decode('utf-8')) for id in ids
        ]

    @classmethod
    def get_by_id(cls, id):
        return Game(get_hashset(redis, 'game:%d' % id))

    @classmethod
    def add(cls, name, players_limit):
        id = Game.get_new_id()
        key = 'game:%d' % id
        data = {
            'id': id,
            'name': name,
            'players_limit': players_limit,
        }
        p = redis.pipeline()
        for (k, v) in data.items():
            p.hset(key, k, v)
        p.lpush('games', id)
        p.execute()

        game = Game(data)
        return game
