from redis_db import (
    ListField, BaseModel, HashField, String, Integer, KeyField, SetField, Float
)


class Game(BaseModel):
    key = 'game'

    data = HashField(
        name=String(),
        players_limit=Integer(mapping_name='playersLimit')
    )
    owner_id = KeyField(Integer(), mapping_name='ownerId')
    user_ids = SetField(Integer(), mapping_name='userIds')

    # game fields
    turn = KeyField(Integer())
    phase = KeyField(Integer())
    step = KeyField(String())
    areas = SetField(String())
    auction = HashField(
        bet=Integer(),
        station=Integer(),
    )
    map = KeyField(String())
    resources = HashField(
        coal=Integer(),
        oil=Integer(),
        waste=Integer(),
        uranium=Integer(),
    )
    stations = ListField(Float())
    #  list of free colors to choose
    reserved_colors = SetField(String())


class Lobby(BaseModel):
    key = 'lobby'


class User(BaseModel):
    key = 'user'

    data = HashField(
        name=String(),
        avatar=String(),
    )
    current_game_id = KeyField(Integer())
    current_lobby_id = KeyField(Integer())


class Player(BaseModel):
    key = 'player'

    color = KeyField(String())
    cash = KeyField(Integer())
    stations = SetField(Integer())
    resources = HashField(
        coal=Integer(),
        oil=Integer(),
        waste=Integer(),
        uranium=Integer(),
    )
    cities = SetField(String())
