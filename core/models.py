from redis_db import BaseModel, HashField, String, Integer, KeyField, SetField


class Game(BaseModel):
    key = 'game'

    data = HashField(
        name=String,
        players_limit=Integer
    )
    owner_id = KeyField(Integer)
    user_ids = SetField(Integer)

    # game fields
    turn = KeyField(Integer)
    phase = KeyField(Integer)
    step = KeyField(String)
    areas = SetField(String)
    auction = HashField(
        bet=Integer,
        station=Integer,
    )
    map = KeyField(String)


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


class Player(BaseModel):
    key = 'player'

    color = KeyField(String)
    cash = KeyField(Integer)
    stations = SetField(Integer)
    resources = HashField(
        coal=Integer,
        oil=Integer,
        waste=Integer,
        uranium=Integer,
    )
    cities = SetField(String)
