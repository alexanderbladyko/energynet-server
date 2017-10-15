from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game, Player
from game.api.base import TurnCheckStep
from game.api.auction.base import BaseAuctionStep
from utils.redis import redis


class AuctionTurnCheckStep(TurnCheckStep):
    step_type = StepTypes.AUCTION


class NoPassFirstAuctionStep(BaseAuctionStep):
    def apply_condition(self, *args, **kwargs):
        return not self.game_has_active_auction() and self.is_first_auction()

    def action(self, pipe, *args, **kwargs):
        raise EnergynetException('No pass in first auction')


class AuctionWinnerStep(BaseAuctionStep):
    game_fields = [Game.auction, Game.order]

    def apply_condition(self, *args, **kwargs):
        return self.game_has_active_auction() \
               and self.is_only_user_for_auction()

    def action(self, pipe, *args, **kwargs):
        winner_id = next(iter(
            self.game.get_users_left_for_auction() - {self.player.id}
        ))
        winner = Player.get_by_id(redis, winner_id, [Player.stations])

        station = self.game.auction.get('station')

        pipe.lrem(Game.stations.key(self.game.id), 0, station)
        pipe.sadd(Player.stations.key(winner_id), station)

        if self.is_stations_over_limit(winner):
            Game.turn.write(pipe, winner_id, self.game.id)
            Game.step.write(pipe, StepTypes.STATION_REMOVE, self.game.id)
        else:
            exclude = self.game.auction_user_ids.union({winner_id})
            next_user_id = self.game.next_player_turn(
                from_start=True, exclude=exclude
            )
            Game.turn.write(pipe, next_user_id, self.game.id)

        Game.auction_passed_user_ids.delete(pipe, self.game.id)
        Game.auction.delete(pipe, self.game.id)


class SavePassedUserStep(BaseAuctionStep):
    def apply_condition(self, *args, **kwargs):
        return self.game_has_active_auction() \
               and not self.is_only_user_for_auction()

    def action(self, pipe, *args, **kwargs):
        Game.auction_passed_user_ids.write(
            pipe, [self.player.id], self.game.id
        )
        next_user_id = self.game.next_player_turn(
            exclude=self.game.auction_off_user_ids, endless=True
        )
        Game.turn.write(pipe, next_user_id, self.game.id)


class RemoveStationOnPassStep(BaseAuctionStep):
    game_fields = [Game.stations, Game.passed_count]

    def apply_condition(self, *args, **kwargs):
        return not self.game_has_active_auction()

    def action(self, pipe, *args, **kwargs):
        pipe.incr(Game.passed_count.key(self.game.id))

        auction_config = self.map_config.get('auction')
        visible_stations = self.game.get_sorted_stations(self.map_config)
        if (
            auction_config.get('removeOnFirstPass')
            and self.game.passed_count == 0
        ):
            pipe.lrem(Game.stations.key(self.game.id), 0, visible_stations[0])

        users_left = self.game.get_users_left_for_auction()
        if auction_config.get('removeOnAnyonePass') and len(users_left) == 1:
            pipe.lrem(Game.stations.key(self.game.id), 0, visible_stations[0])


class PlayerLastPassedStep(BaseAuctionStep):
    def apply_condition(self, *args, **kwargs):
        return not self.game_has_active_auction() \
               and self.is_last_user_for_auction()

    def action(self, pipe, *args, **kwargs):
        Game.step.write(pipe, StepTypes.RESOURCES_BUY, self.game.id)
        next_id = self.game.next_player_turn(reverse=True, from_start=True)
        Game.turn.write(pipe, next_id, self.game.id)
        Game.auction_user_ids.delete(pipe, self.game.id)


class PlayerPassedNoStationStep(BaseAuctionStep):
    def apply_condition(self, *args, **kwargs):
        return not self.game_has_active_auction() \
               and not self.is_last_user_for_auction()

    def action(self, pipe, *args, **kwargs):
        pipe.sadd(Game.auction_user_ids.key(self.game.id), self.player.id)
        next_user_id = self.game.get_next_user_id(
            self.player.id, exclude_ids=self.game.auction_off_user_ids
        )
        Game.turn.write(pipe, next_user_id, self.game.id)


steps = [
    AuctionTurnCheckStep(),
    NoPassFirstAuctionStep(),
    AuctionWinnerStep(),
    SavePassedUserStep(),
    RemoveStationOnPassStep(),
    PlayerLastPassedStep(),
    PlayerPassedNoStationStep(),
]
