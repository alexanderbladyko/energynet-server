import config

from base.exceptions import EnergynetException
from core.models import Game, Player, User
from utils.redis import redis, redis_retry_transaction


class ApiStepRunner:
    def __init__(self, steps):
        self.steps = steps

    @redis_retry_transaction
    def run(self, user_id, data):
        self.init_models(user_id)
        for step in self.steps:
            self._update_models(step)
            step.before_action(**data)

        for step in self.steps:
            if step.apply_condition(**data):
                step.action(pipe)


    def _init_models(self, user_id):
        self.user = User.get_by_id(redis, user_id, [User.current_game_id])
        self.player = Player.get_by_id(redis, user_id, [])
        game_id = self.user.current_game_id
        self.game = Game.get_by_id(redis, game_id, [Game.user_ids])

        self.players = [
            Player.get_by_id(redis, uid, []) for uid in self.game.user_ids
        ]

    def _update_models(self, step):
        self.game.fetch_fields(step.game_fields)
        self.user.fetch_fields(step.user_fields)
        self.player.fetch_fields(step.player_fields)
        for player in self.players:
            player.fetch_fields(step.all_player_fields)


class BaseStep:
    game_fields = []
    user_fields = []
    player_fields = []
    all_player_fields = []

    def init_models(self, **kwargs):
        self.game = kwargs.get('game')
        self.user = kwargs.get('user')
        self.players = kwargs.get('players')

    @property
    def map_config(self):
        return config.config.maps.get(self.game.map)

    def before_action(self):
        pass

    def apply_condition(self):
        return True

    def action(self, pipe):
        pass


class TurnCheckStep(BaseStep):
    game_fields = [Game.turn, Game.step]

    def before_action(self):
        if self.game.turn != self.user.id:
            raise EnergynetException('Its not your move')
        if self.game.step != self.step_type:
            raise EnergynetException('Step is not {}'.format(self.step_type))


class StationCheckStep(BaseStep):
    game_fields = [Game.map, Game.stations]

    def before_action(self, station, *args, **kwargs):
        active_count = self.map_config.get('activeStationsCount')
        if station not in self.game.stations[:active_count]:
            raise EnergynetException('Invalid station')


class AuctionBetCheckStep(BaseStep):
    game_fields = [Game.auction]

    def before_action(self, station, bid, *args, **kwargs):
        previous_bid = self.game.auction.get('bid')
        if previous_bid and previous_bid >= bid:
            raise EnergynetException('Bid is less than previous bid')
        if bid < station:
            raise EnergynetException('Bid is less than station price')
