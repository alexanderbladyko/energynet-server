from base.redis import (
    ObjectList, IdField, DataField, ObjectField, ObjectListField
)
from utils.redis import redis


class Lobby(ObjectList):
    key = 'lobby'

    id = IdField()
    data = DataField([
        'name', 'players_limit'
    ])
    owner_id = ObjectField()
    user_ids = ObjectListField()


class Game(ObjectList):
    key = 'lobby'

    id = IdField()
    data = DataField([
        'name', 'players_limit'
    ])
    owner_id = ObjectField()
    user_ids = ObjectListField()


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

# class Game:
#     def __init__(self, data):
#         self.data = data
#
#     def get_users(self):
#         return GameUsersList(self.data['id'])
#
#
# class GamesList(RedisList):
#     Type = Game
#
#     def __init__(self):
#         super(GamesList, self).__init__('games')
#
#
# class GameUser:
#     def __init__(self, data):
#         self.data = data
#
#     def save_game_id(self, game_id):
#         redis.set('user:%s:game' % str(self.data['id']), game_id)
#
#     def get_game_id(self):
#         return redis.get('user:%s:game' % str(self.data['id'])).decode('utf-8')
#
#     def remove_game_id(self):
#         return redis.delete('user:%s:game' % str(self.data['id']))
#
#
# class GameUsersList(RedisList):
#     Type = GameUser
#
#     def __init__(self, id):
#         super(GameUsersList, self).__init__('games:%s:users' % str(id))
#
#     def get_user_game_id(self, id):
#         user_game_ids = redis.keys('games:*:users:%s' % str(id))
#         if user_game_ids:
#             return user_game_ids[0].decode('utf-8').split(':')[1]
