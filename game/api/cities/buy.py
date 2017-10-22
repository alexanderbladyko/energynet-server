from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game, Player
from game.api.base import BaseStep, TurnCheckStep, NextTurnStep
from game.graph import get_closest_paths


class PlayerHasNoCitiesCheckStep(BaseStep):
    player_fields = [Player.cities]

    def check_parameters(self, cities, *args, **kwargs):
        if set(self.player.cities.keys()).intersection(set(cities)):
            raise EnergynetException('Cities already owned by user')


class CitiesBuyTurnCheckStep(TurnCheckStep):
    step_type = StepTypes.CITIES_BUY


class CitiesBuyStep(BaseStep):
    player_fields = [Player.cash]
    all_player_fields = [Player.cities]
    game_fields = [Game.map, Game.areas]

    def action(self, pipe, cities, *args, **kwargs):
        city_by_name = {
                city['name']: city for city in self.map_config['cities']
                if city['name'] in cities
        }
        if [city for city in city_by_name.values()
                if city['area'] not in self.game.areas]:
            raise EnergynetException('There is city outside of area')

        taken_cities = {}
        for player in self.players:
            for city, slot in player.cities.items():
                if city not in taken_cities:
                    taken_cities[city] = []
                taken_cities[city].append(slot)

        request_cities = {}
        for name, city in city_by_name.items():
            free_slots = set(city['slots']) - set(taken_cities.get(name, []))
            if free_slots:
                request_cities[name] = min(free_slots)
            else:
                raise EnergynetException('No slots for {}'.format(name))

        paths = get_closest_paths(
            self.map_config, self.player.cities.keys(), cities
        )
        price = sum(list(paths.values()) + list(request_cities.values()))
        if self.player.cash < price:
            raise EnergynetException('Not enough cash to buy cities')

        Player.cash.write(pipe, self.player.cash - price, self.player.id)
        pipe.hmset(Player.cities.key(self.player.id), request_cities)


steps = [
    PlayerHasNoCitiesCheckStep(),
    CitiesBuyTurnCheckStep(),
    CitiesBuyStep(),
    NextTurnStep(StepTypes.FINANCE_RECEIVE),
]
