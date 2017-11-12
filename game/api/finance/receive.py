from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game, Player
from game.api.base import BaseStep, TurnCheckStep
from utils.redis import redis


class StationsMatchCheckStep(BaseStep):
    player_fields = [Player.stations]

    def check_parameters(self, stations, *args, **kwargs):
        used_stations = [float(s) for s in stations.keys()]
        if set(used_stations) - self.player.stations != set():
            raise EnergynetException('Stations are not matching')


class FinanceReceiveTurnCheckStep(TurnCheckStep):
    step_type = StepTypes.FINANCE_RECEIVE


class EnoughResourcesCheckStep(BaseStep):
    player_fields = [Player.resources]

    def check_parameters(self, stations, *args, **kwargs):
        next_resources = self.player.resources.copy()
        for resources in stations.values():
            for resource in resources.keys():
                next_resources[resource] -= resources[resource]
        if min(next_resources.values()) < 0:
            raise EnergynetException('Not enough resources')


class RefundStep(BaseStep):
    game_fields = [Game.map]
    player_fields = [Player.stations, Player.cities, Player.cash]

    def action(self, pipe, stations, *args, **kwargs):
        user_stations = self.player.get_user_stations(self.map_config)

        used_stations = [float(s) for s in stations.keys()]

        efficiency = 0
        for user_station in user_stations:
            station = user_station['cost']
            if station not in used_stations:
                continue
            resources = user_station['resources']
            station_efficiency = user_station['efficiency']
            capacity = user_station['capacity']
            req_res = stations[str(float(station))]
            req_resources = set(r for r in req_res.keys() if req_res[r] > 0)
            if req_resources - set(resources) != set():
                raise EnergynetException(
                    'Wrong resources for station {}'.format(station)
                )

            resources_count = sum(req_res.values())
            if resources_count < capacity:
                raise EnergynetException(
                    'Not enough resources for station {}'.format(station)
                )
            efficiency += station_efficiency

        heated_cities = min(efficiency, len(self.player.cities.keys()))
        payment_config = self.map_config.get('payment')

        payment = (
            payment_config[heated_cities]
            if heated_cities < len(payment_config)
            else payment_config[-1]
        )
        Player.cash.write(pipe, self.player.cash + payment, self.player.id)


class DecreasePlayerResourcesStep(BaseStep):
    player_fields = [Player.resources]

    def action(self, pipe, stations, *args, **kwargs):
        next_resources = self.player.resources.copy()
        for resources in stations.values():
            for resource in resources.keys():
                next_resources[resource] -= resources[resource]
        Player.resources.write(pipe, next_resources, self.player.id)


class NextUserTurnStep(BaseStep):
    game_fields = [Game.step, Game.turn, Game.order]

    def apply_condition(self, *args, **kwargs):
        return self.game.order.index(self.player.id) != 0

    def action(self, pipe, *args, **kwargs):
        next_id = self.game.next_player_turn(reverse=True)
        Game.turn.write(pipe, next_id, self.game.id)


class StartAuctionReorderStep(BaseStep):
    game_fields = [Game.step, Game.turn, Game.order]

    def apply_condition(self, *args, **kwargs):
        return self.game.order.index(self.player.id) == 0

    def action(self, pipe, *args, **kwargs):
        new_order = self.game.get_new_order(redis)
        Game.order.delete(pipe, self.game.id)
        Game.order.write(pipe, new_order, self.game.id)
        Game.turn.write(pipe, new_order[0], self.game.id)
        Game.step.write(pipe, StepTypes.AUCTION, self.game.id)


class MaxStationToBackStep(BaseStep):
    game_fields = [Game.stations, Game.phase]

    def apply_condition(self, *args, **kwargs):
        return self.game.order.index(self.player.id) == 0 \
               and self.game.phase in [1, 2]

    def action(self, pipe, *args, **kwargs):
        visible_stations = self.map_config.get('visibleStationsCount')
        max_station = max(self.game.stations[:visible_stations])
        pipe.lrem(Game.stations.key(self.game.id), 1, max_station)
        pipe.rpush(Game.stations.key(self.game.id), max_station)


class ResourcesRefillStep(BaseStep):
    game_fields = [Game.resources, Game.phase]

    def apply_condition(self, *args, **kwargs):
        return self.game.order.index(self.player.id) == 0

    def action(self, pipe, *args, **kwargs):
        game_resources_left = dict(
            (resource, self._get_resource_count(resource, count))
            for resource, count in self.game.resources.items()
        )
        Game.resources.write(pipe, game_resources_left, self.game.id)

    def _get_resource_count(self, resource, count):
        limit = self.map_config.get('resourceLimits').get(resource)
        refill = self.map_config.get('refill')
        phase_refill = refill[self.game.phase - 1]
        users_count = len(self.game.user_ids)
        result_count = count + phase_refill.get(resource)[users_count - 1]
        if result_count > limit:
            return limit
        return result_count


class ReorderStep(BaseStep):
    def apply_condition(self, *args, **kwargs):
        return self.game.order.index(self.player.id) == 0

    def action(self, pipe, *args, **kwargs):
        new_order = self.game.get_new_order(redis, self.player.id)
        Game.order.delete(pipe, self.game.id)
        Game.order.write(pipe, new_order, self.game.id)


steps = [
    StationsMatchCheckStep(),
    FinanceReceiveTurnCheckStep(),
    EnoughResourcesCheckStep(),
    RefundStep(),
    DecreasePlayerResourcesStep(),
    NextUserTurnStep(),
    StartAuctionReorderStep(),
    MaxStationToBackStep(),
    ResourcesRefillStep(),
    ReorderStep(),
]
