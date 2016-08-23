from utils.redis import redis


class BaseField(object):
    """Base redis field"""
    def __init__(self):
        super(BaseField, self).__init__()

    def get_value(self, key, id, name, p):
        value = p.get(key+':'+str(id)+':'+name)
        return value and value.decode('utf-8')

    def set_value(self, key, id, name, value, p):
        p.set(key+':'+str(id)+':'+name, value)

    def delete(self, key, id, name, p):
        p.delete(key+':'+str(id)+':'+name)


class IdField(BaseField):
    """Id field"""
    def __init__(self):
        super(IdField, self).__init__()

    def get_value(self, key, id, name, p):
        return id

    def set_value(self, key, id, name, value, p):
        pass

    def delete(self, key, id, name):
        pass


class DataField(BaseField):
    """Data field"""
    def __init__(self, fields):
        self.fields = fields

    def get_hashset(self, key, p):
        hashset_items = p.hgetall(key).items()
        return dict(
            (k.decode('utf-8'), v.decode('utf-8')) for (k, v) in hashset_items
        )

    def get_value(self, key, id, name, p):
        data = self.get_hashset(key+':'+str(id)+':'+name, p)
        if not data:
            return None
        result = {}
        for field in self.fields:
            result[field] = data.get(field)

        return result

    def set_value(self, key, id, name, value, p):
        if not value:
            return
        if not isinstance(value, dict):
            return
        item_key = key+':'+str(id)+':'+name
        for field in self.fields:
            if field in value:
                p.hset(item_key, field, value[field])


class ObjectField(BaseField):
    pass


class ObjectListField(BaseField):
    """Object list field"""
    def get_value(self, key, id, name, p):
        return p.lrange(key+':'+str(id)+':'+name, 0, -1)

    def set_value(self, key, id, name, value, p):
        item_key = key+':'+str(id)+':'+name
        p.delete(item_key)
        p.rpush(item_key, value)

    def delete(self, key, id, name, p):
        p.delete(key+':'+str(id)+':'+name)


class ObjectList(object):
    def __init__(self):
        self._fields = self.get_all_fields()
        for field_name, field in self._fields:
            setattr(self, field_name, None)

    @classmethod
    def get_all_fields(cls):
        return [
            (name, value) for name, value in vars(cls).items()
            if isinstance(value, BaseField)
        ]

    @classmethod
    def get_next_id(cls, p=None):
        p = p or redis
        index_key = cls.key + ':index'
        return p.incr(index_key)

    @classmethod
    def get_all(cls, fields=None, p=None):
        p = p or redis
        ids = p.smembers(cls.key)

        fields = fields if fields else cls.get_all_fields()

        for id in ids:
            instance = cls()
            setattr(instance, 'id', id)
            for field_name, field in fields:
                value = field.get_value(cls.key, id, field_name, p)
                setattr(instance, field_name, value)
            yield instance

    @classmethod
    def get_by_id(cls, id, fields=None, p=None):
        p = p or redis
        if not p.sismember(cls.key, id):
            return None
        fields = fields if fields else cls.get_all_fields()
        instance = cls()
        setattr(instance, 'id', id)
        for field_name, field in fields:
            value = field.get_value(cls.key, id, field_name, p)
            setattr(instance, field_name, value)
        return instance

    def save(self, pipeline=None):
        p = pipeline or redis.pipeline()
        fields = self.get_all_fields()

        if not self.id or isinstance(self.id, IdField):
            self.id = self.get_next_id(p)

        p.sadd(self.key, self.id)

        for name, field in fields:
            value = getattr(self, name)
            if not isinstance(value, BaseField):
                field.set_value(self.key, self.id, name, value, p)

        if not pipeline:
            p.execute()

    def delete(self, pipeline=None):
        p = pipeline or redis.pipeline()
        fields = self.get_all_fields()

        p.srem(self.key, self.id)

        for name, field in fields:
            field.delete(self.key, self.id, name, p)

        if not pipeline:
            p.execute()


# class RedisList(object):
#     def __init__(self, key):
#         self.key = key
#
#     def get_new_id(self):
#         index_key = self.key + ':index'
#         return redis.incr(index_key)
#
#     def add(self, instance):
#         id = instance.data['id']
#         item_key = self.key + ':' + str(id)
#         p = redis.pipeline()
#         for (k, v) in instance.data.items():
#             p.hset(item_key, k, v)
#         p.lpush(self.key, id)
#         p.execute()
#
#     def remove(self, id):
#         item_key = self.key + ':' + str(id)
#         p = redis.pipeline()
#         p.delete(item_key)
#         p.lrem(self.key, str(id), 1)
#         p.execute()
#
#     def get_all(self):
#         ids = redis.lrange(self.key, 0, -1)
#         return [self.get_by_id(id.decode('utf-8')) for id in ids]
#
#     def get_by_id(self, id):
#         item_key = self.key + ':' + str(id)
#         return self.Type(self.get_hashset(item_key))
