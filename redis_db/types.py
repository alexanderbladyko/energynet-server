class Base:
    def __init__(self, mapping_name=None, *args, **kwargs):
        self.mapping_name = mapping_name

    cast_from_fn = None

    @classmethod
    def cast_from(cls, value):
        return cls.cast_from_fn(value) if cls.cast_from_fn else value

    cast_to_fn = None

    @classmethod
    def cast_to(cls, value):
        return cls.cast_to_fn(value) if cls.cast_to_fn else value


class Integer(Base):
    def cast_from_fn(v):
        return int(v) if v else None


class String(Base):
    def cast_from_fn(v):
        return v.decode('utf-8') if v else None

    def cast_to_fn(v):
        return v.encode('utf-8') if v else None
