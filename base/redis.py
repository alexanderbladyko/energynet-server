from utils.redis import redis


class BaseField(object):
    """Base redis field"""
    def __init__(self):
        super(BaseField, self).__init__()

    def get_value(self, key, id, p):
        value = p.get(key)
        if value is not None:
            return value.decode('utf-8')

    def set_value(self, key, id, value, p):
        if value is not None:
            p.set(key, value)
        else:
            p.delete(key)

    def delete(self, key, id, p):
        p.delete(key)


class IdField(BaseField):
    """Id field"""
    def __init__(self):
        super(IdField, self).__init__()

    def get_value(self, key, id, p):
        return id

    def set_value(self, key, id, value, p):
        pass

    def delete(self, key, id, p):
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

    def get_value(self, key, id, p):
        data = self.get_hashset(key, p)
        if not data:
            return None
        result = {}
        for field in self.fields:
            result[field] = data.get(field)

        return result

    def set_value(self, key, id, value, p):
        if not value:
            return
        if not isinstance(value, dict):
            return
        for field in self.fields:
            if field in value:
                p.hset(key, field, value[field])


class ObjectField(BaseField):
    def get_value(self, key, id, p):
        value = super(ObjectField, self).get_value(key, id, p)
        if value is not None:
            return int(value)


class ObjectListField(BaseField):
    """Object list field"""
    def get_value(self, key, id, p):
        values = p.lrange(key, 0, -1)
        if values:
            return [int(v.decode('utf-8')) for v in values]

    def set_value(self, key, id, value, p):
        p.delete(key)
        if value is not None:
            p.lpush(key, *value)

    def delete(self, key, id, p):
        p.delete(key)


class ObjectList(object):
    def __init__(self, fields=None):
        self._fields = self.get_all_fields(fields)
        for field_name, field in self.get_all_fields():
            setattr(self, field_name, None)

    @classmethod
    def get_key(cls, id, field_name):
        return cls.key+':'+str(id)+':'+field_name

    @classmethod
    def get_all_fields(cls, fields=None):
        if fields:
            return [
                (name, value) for name, value in vars(cls).items()
                if isinstance(value, BaseField) and value in fields
            ]
        else:
            return [
                (name, value) for name, value in vars(cls).items()
                if isinstance(value, BaseField)
            ]

    @classmethod
    def get_next_id(cls):
        return redis.incr(cls.key + ':index')

    @classmethod
    def get_all(cls, fields=None):
        ids = redis.smembers(cls.key)

        all_fields = cls.get_all_fields(fields)

        return [cls._get_by_id(int(id), fields, all_fields) for id in ids]

    @classmethod
    def get_by_ids(cls, ids, fields=None):
        all_fields = cls.get_all_fields(fields)

        return [cls._get_by_id(int(id), fields, all_fields) for id in ids]

    @classmethod
    def get_by_id(cls, id, fields=None):
        if not cls.contains(id):
            return None
        all_fields = cls.get_all_fields(fields)
        return cls._get_by_id(int(id), fields, all_fields)

    @classmethod
    def contains(cls, id):
        return redis.sismember(cls.key, id)

    @classmethod
    def _get_by_id(cls, id, fields, all_fields):
        instance = cls(fields)
        setattr(instance, 'id', id)
        for field_name, field in all_fields:
            value = field.get_value(cls.get_key(id, field_name), id, redis)
            if value is not None:
                setattr(instance, field_name, value)
        return instance

    def save(self, p=None):
        pipeline = p if p is not None else redis.pipeline()

        if not self.id or isinstance(self.id, IdField):
            self.id = self.get_next_id()

        pipeline.sadd(self.key, self.id)

        for name, field in self._fields:
            value = getattr(self, name)
            if not isinstance(value, BaseField):
                key = self.get_key(self.id, name)
                field.set_value(key, self.id, value, pipeline)

        if p is None:
            pipeline.execute()

    def delete(self, p=None):
        pipeline = p if p is not None else redis.pipeline()

        pipeline.srem(self.key, self.id)

        for name, field in self._fields:
            field.delete(self.get_key(self.id, name), self.id, pipeline)

        if not p:
            pipeline.execute()

    def serialize(self):
        fields = self.get_all_fields()

        data = {}
        for name, field in fields:
            value = getattr(self, name)
            if value and not isinstance(value, BaseField):
                data[name] = value
        return data
