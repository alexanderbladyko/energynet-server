from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game, Player
from game.api.base import BaseStep, TurnCheckStep
from game.api.auction.base import BaseAuctionStep
from utils.redis import redis


class AuctionTurnCheckStep(TurnCheckStep):
    step_type = StepTypes.AUCTION


class StationCheckStep(BaseStep):
    game_fields = [Game.map, Game.stations]

    def check_parameters(self, station, *args, **kwargs):
        active_count = self.map_config.get('activeStationsCount')
        if station not in self.game.stations[:active_count]:
            raise EnergynetException('Invalid station')


class AuctionBidCheckStep(BaseStep):
    game_fields = [Game.auction]

    def check_parameters(self, station, bid, *args, **kwargs):
        previous_bid = self.game.auction.get('bid')
        if previous_bid and previous_bid >= bid:
            raise EnergynetException('Bid is less than previous bid')
        if bid < station:
            raise EnergynetException('Bid is less than station price')


class AuctionLastUserStep(BaseAuctionStep):
    def apply_condition(self, station, bid):
        return self.is_last_user_for_auction()

    def action(self, pipe, station, bid):
        pipe.lrem(Game.stations.key(self.game.id), 0, float(station))
        pipe.sadd(Player.stations.key(self.player.id), station)
        Game.auction_user_ids.delete(pipe, self.game.id)


class StationRemoveStep(BaseAuctionStep):
    game_fields = BaseAuctionStep.game_fields + [Game.order, Game.phase]
    player_fields = [Player.stations]

    def apply_condition(self, *args, **kwargs):
        return self.is_last_user_for_auction() \
               and self.is_stations_over_limit()

    def action(self, pipe, station, bid):
        Game.step.write(pipe, StepTypes.STATION_REMOVE, self.game.id)


class FirstAuctionReorderStep(BaseAuctionStep):
    def apply_condition(self, *args, **kwargs):
        return self.is_last_user_for_auction() \
               and not self.is_stations_over_limit() \
               and self.is_first_auction()

    def action(self, pipe, station, bid):
        new_order = self.game.get_new_order(redis, self.player.id, station)
        Game.order.delete(pipe, self.game.id)
        Game.order.write(pipe, new_order, self.game.id)
        Game.turn.write(pipe, new_order[-1], self.game.id)
        Game.step.write(pipe, StepTypes.RESOURCES_BUY, self.game.id)
        Game.phase.write(pipe, 1, self.game.id)


class LastBidNextUserStep(BaseAuctionStep):
    def apply_condition(self, *args, **kwargs):
        return self.is_last_user_for_auction() \
               and not self.is_stations_over_limit() \
               and not self.is_first_auction()

    def action(self, pipe, station, bid):
        Game.step.write(pipe, StepTypes.RESOURCES_BUY, self.game.id)
        next_id = self.game.next_player_turn(reverse=True, from_start=True)
        Game.turn.write(pipe, next_id, self.game.id)


class ActiveStationBidStep(BaseAuctionStep):
    def apply_condition(self, *args, **kwargs):
        return not self.is_last_user_for_auction()

    def action(self, pipe, station, bid):
        Game.auction.write(pipe, {
            'bid': bid,
            'station': station,
            'user_id': self.player.id,
        }, self.game.id)

        next_user_id = self.game.get_next_user_id(
            self.player.id, exclude_ids=self.game.auction_off_user_ids
        )
        Game.turn.write(pipe, next_user_id, self.game.id)


steps = [
    AuctionTurnCheckStep(),
    StationCheckStep(),
    AuctionBidCheckStep(),
    AuctionLastUserStep(),
    StationRemoveStep(),
    FirstAuctionReorderStep(),
    LastBidNextUserStep(),
    ActiveStationBidStep(),
]
