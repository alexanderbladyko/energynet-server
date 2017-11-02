from core.constants import Resources
from redis_db import (
    ListField, BaseModel, HashField, String, Integer, KeyField, SetField,
    Float, DictField,
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

    @property
    def auction_off_user_ids(self):
        return self.auction_user_ids.union(self.auction_passed_user_ids)

    def next_player_turn(
        self, from_start=False, reverse=False, exclude=None, endless=False
    ):
        player_ids = self.order.copy()
        if reverse:
            player_ids.reverse()
        exclude_ids = exclude or []

        index = player_ids.index(self.turn) + 1
        if from_start:
            next_ids = player_ids
        else:
            next_ids = player_ids[index:]
            if endless:
                next_ids += player_ids[:index]

        for player_id in next_ids:
            if player_id not in exclude_ids:
                return player_id

    def get_next_user_id(self, user_id, exclude_ids=None):
        index = self.order.index(user_id) + 1
        next_ids = self.order[index:] + self.order[:index]
        if exclude_ids:
            for user_id in next_ids:
                if user_id not in exclude_ids:
                    return user_id
        else:
            return next_ids[0]

    def get_users_left_for_auction(self, with_passed=True):
        left_users = self.user_ids - self.auction_user_ids
        if with_passed:
            return left_users - self.auction_passed_user_ids
        return left_users

    def get_sorted_stations(self, map_config):
        visible_count = map_config.get('visibleStationsCount')

        return sorted(self.stations[i] for i in range(visible_count))

    def get_new_order(self, redis, player_id=None, station=None):
        data_by_users = self.get_order_data_by_users(redis)
        if player_id and station:
            data_by_users[player_id] = (
                data_by_users[player_id][0],
                max(data_by_users[player_id][1], station)
            )
        return [u_id for u_id, _ in sorted(
            data_by_users.items(), key=lambda d: d[1], reverse=True
        )]

    def get_order_data_by_users(self, redis):
        return {
            id: Player.get_order_data(redis, id) for id in self.user_ids
        }

    def get_resource_price(self, map_config, new_resources):
        groups = map_config.get('resourceGroup')
        limits = map_config.get('resourceLimits')
        price = 0
        for resource in Resources.ALL:
            group = groups.get(resource)
            limit = limits.get(resource)
            exists = self.resources.get(resource, 0)
            desired = new_resources.get(resource, 0)
            if exists < desired:
                return False, 0
            for i in range(desired):
                resource_position = limit - exists + i
                next_price = int(resource_position / group) + 1
                price += next_price
        return True, price


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
    cities = DictField(String(), Integer())

    def get_user_stations(self, map_config):
        stations_config = map_config.get('stations')
        return [s for s in stations_config if s.get('cost') in self.stations]

    def can_hold_new_resources(self, map_config, new_resources):
        user_stations = self.get_user_stations(map_config)
        # creating resources slots grouped by count of resources
        slots_by_count = {}
        for station in user_stations:
            resources = station.get('resources')
            count = len(resources)
            if not slots_by_count.get(count):
                slots_by_count[count] = []
            slots_by_count[count].extend([
                resources for _ in range(station.get('capacity') * 2)
            ])

        # sort every slots in group
        for count in slots_by_count.keys():
            slots_by_count[count] = sorted(slots_by_count[count])

        # trying to spread resources
        for resource in sorted(Resources.ALL):
            player_resources = self.resources.get(resource, 0) or 0
            total = (
                player_resources + new_resources.get(resource, 0)
            )
            for resource_count in range(len(Resources.ALL)):
                i = 0
                while i < len(slots_by_count.get(resource_count + 1, [])):
                    slot = slots_by_count.get(resource_count + 1, [])[i]
                    if resource in slot and total > 0:
                        del slots_by_count[resource_count + 1][i]
                        total -= 1
                    else:
                        i += 1

            if total > 0:
                return False, 'Not enough space for {}'.format(resource)

        return True, ''

    @classmethod
    def get_order_data(cls, redis, player_id):
        cities_count = redis.hlen(cls.cities.key(player_id))
        max_stations_count = max(cls.stations.read(redis, player_id))
        return (cities_count, max_stations_count)
