from core.models import Game
from game.api.base import BaseStep


class BaseAuctionStep(BaseStep):
    game_fields = [
        Game.auction_user_ids, Game.auction_passed_user_ids, Game.phase,
        Game.map
    ]

    def is_last_user_for_auction(self):
        left_users = self.game.get_users_left_for_auction(with_passed=False)
        return left_users == {self.player.id}

    def is_first_auction(self):
        return self.game.phase == 0

    def is_stations_over_limit(self, player=None):
        player = player or self.player
        user_stations_count = self.map_config.get('userStationsCount')
        stations_limit = user_stations_count[len(self.game.user_ids) - 1]
        return len(player.stations) == stations_limit

    def game_has_active_auction(self):
        return self.game.auction.get('station') is not None

    def is_only_user_for_auction(self):
        users_left = self.game.get_users_left_for_auction() - {self.player.id}
        return len(users_left) == 1
