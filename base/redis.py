from utils.redis import redis


class RedisList(object):
    def __init__(self, key):
        self.key = key

    def get_new_id(self):
        index_key = self.key + ':index'
        return redis.incr(index_key)

    def add(self, instance):
        id = instance.data['id']
        item_key = self.key + ':' + str(id)
        p = redis.pipeline()
        for (k, v) in instance.data.items():
            p.hset(item_key, k, v)
        p.lpush(self.key, id)
        p.execute()

    def remove(self, id):
        item_key = self.key + ':' + id
        p = redis.pipeline()
        p.delete(item_key)
        p.lrem(self.key, id)
        p.execute()

    def get_all(self):
        ids = redis.lrange(self.key, 0, -1)
        return [self.get_by_id(id.decode('utf-8')) for id in ids]

    def get_by_id(self, id):
        item_key = self.key + ':' + str(id)
        return self.Type(self.get_hashset(item_key))

    def get_hashset(self, key):
        hashset_items = redis.hgetall(key).items()
        return dict(
            (k.decode('utf-8'), v.decode('utf-8')) for (k, v) in hashset_items
        )
