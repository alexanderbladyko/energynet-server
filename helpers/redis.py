def get_hashset(redis, key):
    hashset_items = redis.hgetall(key).items()
    return dict(
        (k.decode('utf-8'), v.decode('utf-8')) for (k, v) in hashset_items
    )
