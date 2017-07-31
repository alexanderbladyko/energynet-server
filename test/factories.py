from core.models import User, Game, Lobby
from utils.redis import redis


class BaseFactory:
    @classmethod
    def create(cls, *args, **kwargs):
        instance = cls.model()
        instance.id = redis.incr(cls.model.index())

        for name, field in cls.model.get_all_fields():
            if name in kwargs:
                value = kwargs.get(name)
            else:
                value = getattr(cls, name, None)
            setattr(instance, name, value)
            if value is not None:
                field.write(redis, value, instance.id)

        redis.sadd(cls.model.key, instance.id)

        return instance


class UserFactory(BaseFactory):
    model = User

    data = {
        'name': 'user',
        'avatar': 'avatar'
    }

    @classmethod
    def ensure_from_db(cls, db_user, *args, **kwargs):
        instance = cls.model()

        instance.id = db_user.id

        for name, field in cls.model.get_all_fields():
            if name == 'data':
                field.write(redis, {
                    'name': db_user.name,
                    'avatar': None,
                }, instance.id)
                continue
            value = kwargs.get(name) or getattr(cls, name, None)
            setattr(instance, name, value)
            if value is not None:
                field.write(redis, value, instance.id)

        return instance


class GameFactory(BaseFactory):
    model = Game

    data = {
        'name': 'game',
        'players_limit': 5
    }


class LobbyFactory(BaseFactory):
    model = Lobby

    @classmethod
    def create(cls, game_id, *args, **kwargs):
        instance = Lobby()
        instance.id = game_id
        redis.sadd(cls.model.key, instance.id)

        return instance
