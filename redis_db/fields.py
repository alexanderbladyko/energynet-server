from redis_db.types import String


class BaseField:
    def __init__(self, mapping_name=None, *args, **kwargs):
        self.base = None
        self.name = None
        self.mapping_name = mapping_name

    def key(self, id=None):
        if id:
            return '{}:{}:{}'.format(self.base, id, self.name)
        return '{}:{}'.format(self.base, self.name)

    def read(self, pipe, id=None):
        return pipe.get(self.key(id))

    def write(self, pipe, value, id=None):
        if value is not None:
            pipe.set(self.key(id), value)
        else:
            pipe.delete(self.key(id))

    def delete(self, pipe, id=None):
        pipe.delete(self.key(id))


class KeyField(BaseField):
    def __init__(self, type, *args, **kwargs):
        super(KeyField, self).__init__(*args, **kwargs)
        self.type = type

    def read(self, pipe, id=None):
        return self.type.cast_from(pipe.get(self.key(id)))


class SetField(BaseField):
    def __init__(self, type, *args, **kwargs):
        super(SetField, self).__init__(*args, **kwargs)
        self.type = type

    def read(self, pipe, id=None):
        return set(self.type.cast_from(m) for m in pipe.smembers(self.key(id)))

    def write(self, pipe, value: set, id=None):
        pipe.sadd(self.key(id), *value)


class ListField(BaseField):
    def __init__(self, type, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)
        self.type = type

    def read(self, pipe, id=None):
        return [
            self.type.cast_from(m) for m in pipe.lrange(self.key(id), 0, -1)
        ]

    def write(self, pipe, value: list, id=None):
        pipe.rpush(self.key(id), *value)


class HashField(BaseField):
    def __init__(self, *args, **kwargs):
        super(HashField, self).__init__(*args, **kwargs)
        self.fields = kwargs

    def read(self, pipe, id=None):
        data = pipe.hgetall(self.key(id))
        return {
            k: f.cast_from(data.get(String.cast_to(k)))
            for k, f in self.fields.items()
        }

    def write(self, pipe, value: set, id=None):
        pipe.hmset(self.key(id), {
            k: value.get(k)
            for k, f in self.fields.items() if value.get(k) is not None
        })


class FieldNameResolverMetaClass(type):
    '''
    Meta class which adds field name to descriptor.
    '''
    def __new__(cls, classname, bases, classDict):
        if 'key' not in classDict:
            raise Exception('Class should have string key')
        class_key = classDict.get('key')
        for name, attr in classDict.items():
            if isinstance(attr, BaseField):
                attr.base = class_key
                attr.name = name
        return type.__new__(cls, classname, bases, classDict)


class BaseModel(metaclass=FieldNameResolverMetaClass):
    key = ''

    @classmethod
    def get_key(cls, field: BaseField, id: int=None):
        return cls.field.key(id)

    @classmethod
    def get_by_id(cls, pipe, id, fields=None):
        instance = cls()
        instance.id = id
        for name, field in cls.get_all_fields():
            if fields:
                if field in fields:
                    setattr(instance, name, field.read(pipe, id))
                else:
                    setattr(instance, name, None)
            else:
                setattr(instance, name, field.read(pipe, id))
        return instance

    @classmethod
    def get_all_fields(cls, fields=None):
        if fields:
            return [
                (name, value) for name, value in vars(cls).items()
                if isinstance(value, BaseField) and value in fields
            ]
        return [
            (name, value) for name, value in vars(cls).items()
            if isinstance(value, BaseField)
        ]

    @classmethod
    def index(cls):
        return '{}:index'.format(cls.key)

    @classmethod
    def delete(cls, pipe, id):
        for _, field in cls.get_all_fields():
            field.delete(pipe, id)

    def remove(self, pipe):
        for _, field in self.get_all_fields():
            field.delete(pipe, self.id)

    def serialize(self, fields=None):
        obj = {
            'id': self.id,
        }
        for name, field in self.get_all_fields(fields):
            value = getattr(self, name, None)
            key_name = field.mapping_name or name
            if isinstance(value, set):
                value = list(value)
            if isinstance(value, dict):
                obj[key_name] = {}
                for name, sub_field in field.fields.items():
                    sub_key_name = sub_field.mapping_name or name
                    obj[key_name][sub_key_name] = value.get(name)
                continue
            obj[key_name] = value
        return obj
