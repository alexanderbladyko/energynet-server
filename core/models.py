from redis_db import BaseModel, HashField, String, Integer, KeyField, SetField


class Game(BaseModel):
    key = 'game'

    data = HashField(
        name=String,
        players_limit=Integer
    )
    owner_id = KeyField(Integer)
    user_ids = SetField(Integer)

    def add_user(self, user_id):
        if not self.user_ids:
            self.user_ids = []
        self.user_ids.append(int(user_id))

    def remove_user(self, user_id):
        self.user_ids.remove(int(user_id))


class Lobby(BaseModel):
    key = 'lobby'


class User(BaseModel):
    key = 'user'

    data = HashField(
        name=String,
        avatar=String,
    )
    current_game_id = KeyField(Integer)
    current_lobby_id = KeyField(Integer)
    game_data = HashField(
        color=String,
        money=Integer
    )
