from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game, Player
from game.api.base import BaseStep, TurnCheckStep


class BaseStationRemoveStep(BaseStep):
    game_fields = [
        Game.auction_user_ids, Game.auction_passed_user_ids, Game.phase,
        Game.map, Game.order,
    ]

    def is_last_user_for_auction(self):
        left_users = self.game.get_users_left_for_auction(with_passed=False)
        return left_users == {self.player.id}


class StationCheckStep(BaseStep):
    player_fields = [Player.stations]

    def check_parameters(self, station, *args, **kwargs):
        if station not in self.player.stations:
            raise EnergynetException('Invalid station')


class StationRemoveTurnCheckStep(TurnCheckStep):
    step_type = StepTypes.STATION_REMOVE


class StationRemoveStep(BaseStep):
    def action(self, pipe, station, *args, **kwargs):
        pipe.srem(Player.stations.key(self.player.id), station)


class LastPlayerRemovedStationStep(BaseStationRemoveStep):
    def apply_condition(self, *args, **kwargs):
        return self.is_last_user_for_auction()

    def action(self, pipe, *args, **kwargs):
        Game.step.write(pipe, StepTypes.RESOURCES_BUY, self.game.id)
        next_id = self.game.next_player_turn(reverse=True, from_start=True)
        Game.turn.write(pipe, next_id, self.game.id)
        Game.auction_user_ids.delete(pipe, self.game.id)


class PlayerPassedNoStationStep(BaseStationRemoveStep):
    def apply_condition(self, *args, **kwargs):
        return not self.is_last_user_for_auction()

    def action(self, pipe, *args, **kwargs):
        Game.step.write(pipe, StepTypes.AUCTION, self.game.id)
        exclude = self.game.auction_user_ids.union({self.player.id})
        next_id = self.game.next_player_turn(from_start=True, exclude=exclude)
        Game.turn.write(pipe, next_id, self.game.id)


steps = [
    StationCheckStep(),
    StationRemoveTurnCheckStep(),
    StationRemoveStep(),
    LastPlayerRemovedStationStep(),
    PlayerPassedNoStationStep(),
]
