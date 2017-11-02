from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game, Player
from game.api.base import BaseStep, TurnCheckStep, NextTurnStep


class ResourcesBuyTurnCheckStep(TurnCheckStep):
    step_type = StepTypes.RESOURCES_BUY


class PlayerCanHoldSuchResourcesCheckStep(BaseStep):
    game_fields = [Game.map]
    player_fields = [Player.stations, Player.resources]

    def check_parameters(self, resources, *args, **kwargs):
        can_hold, reason = self.player.can_hold_new_resources(
            self.map_config, resources
        )
        if not can_hold:
            raise EnergynetException(reason)


class ResourcePriceStep(BaseStep):
    game_fields = [Game.resources]
    player_fields = [Player.cash]

    def check_parameters(self, resources, *args, **kwargs):
        can_purchase, price = self.game.get_resource_price(
            self.map_config, resources
        )
        if not can_purchase:
            raise EnergynetException('Not enough resources')

        if self.player.cash < price:
            raise EnergynetException('Not enough cash')

    def action(self, pipe, resources, *args, **kwargs):
        _, price = self.game.get_resource_price(
            self.map_config, resources
        )
        Player.cash.write(pipe, self.player.cash - price, self.player.id)


class DecreaseGameResourcesStep(BaseStep):
    def action(self, pipe, resources, *args, **kwargs):
        game_resources_left = dict(
            (resource, count - resources.get(resource, 0))
            for resource, count in self.game.resources.items()
        )
        Game.resources.write(pipe, game_resources_left, self.game.id)


class DecreasePlayerResourcesStep(BaseStep):
    def action(self, pipe, resources, *args, **kwargs):
        player_resources_now = dict(
            (resource, (count or 0) + resources.get(resource, 0))
            for resource, count in self.player.resources.items()
        )
        Player.resources.write(pipe, player_resources_now, self.player.id)


steps = [
    ResourcesBuyTurnCheckStep(),
    PlayerCanHoldSuchResourcesCheckStep(),
    ResourcePriceStep(),
    DecreaseGameResourcesStep(),
    DecreasePlayerResourcesStep(),
    NextTurnStep(StepTypes.CITIES_BUY),
]
