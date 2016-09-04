from flask_login import current_user

from base.redis import (
    ObjectList, IdField, DataField, ObjectField, ObjectListField
)
from utils.redis import redis


class Game(ObjectList):
    key = 'game'

    id = IdField()
    data = DataField([
        'name', 'players_limit'
    ])
    owner_id = ObjectField()
    user_ids = ObjectListField()

    def add_user(self, user_id, p):
        p.rpush(Game.get_key(self.id, 'user_ids'), user_id)
        if not self.user_ids:
            self.user_ids = []
        self.user_ids.append(int(user_id))

    def remove_user(self, user_id, p):
        p.lrem(Game.get_key(self.id, 'user_ids'), 1, user_id)
        self.user_ids.remove(int(user_id))


class Lobby(ObjectList):
    key = 'lobby'

    id = IdField()


class User(ObjectList):
    key = 'user'

    id = IdField()
    data = DataField([
        'name', 'avatar'
    ])
    current_game_id = ObjectField()
    current_lobby_id = ObjectField()
    game_data = DataField([
        'color', 'money'
    ])

    @classmethod
    def ensure(cls, pipeline=None):
        if not redis.sismember(cls.key, current_user.id):
            p = pipeline or redis.pipeline()

            user = User()
            user.id = current_user.id
            user.data = {
                'name': current_user.name,
            }
            user.save(p)

            if not pipeline:
                p.execute()
