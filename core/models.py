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
    order = ListField(Integer())

    # game fields
    turn = KeyField(Integer())
    phase = KeyField(Integer())
    step = KeyField(String())
    areas = SetField(String())
    auction = HashField(
        bid=Integer(),
        station=Float(),
        user_id=Integer(mapping_name='userId')
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
    #  set of out-of-auction userIds
    auction_user_ids = SetField(Integer())
    #  set of userIds folded auction
    auction_passed_user_ids = SetField(Integer())
    passed_count = KeyField(Integer())

    def get_next_user_id(self, user_id, exclude_ids=None):
        index = self.order.index(user_id) + 1
        next_ids = self.order[index:] + self.order[:index]
        if exclude_ids:
            for user_id in next_ids:
                if user_id not in exclude_ids:
                    return user_id
        else:
            return next_ids[0]

    def has_active_station_in_auction(self):
        return self.auction.get('station') is not None

    def get_users_left_for_auction(self):
        return (
            self.user_ids -
            self.auction_user_ids -
            self.auction_passed_user_ids
        )

    @property
    def auction_off_user_ids(self):
        return self.auction_user_ids.union(self.auction_passed_user_ids)


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
    stations = SetField(Float())
    resources = HashField(
        coal=Integer(),
        oil=Integer(),
        waste=Integer(),
        uranium=Integer(),
    )
    cities = SetField(String())
