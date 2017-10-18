import config

from base.exceptions import EnergynetException
from core.models import Game, Player, User
from game.logic import notify_game_players
from utils.redis import redis, redis_retry_transaction


class ApiStepRunner:
    def __init__(self, steps):
        self.steps = steps

    def run(self, user_id, data, *args, **kwargs):
        self._init_models(user_id)
        pipe = redis.pipeline()
        self._transaction(pipe, data)

        return {'success': True}

    @redis_retry_transaction()
    def _transaction(self, pipe, data):
        for action_step in self.steps:
            self._update_models(action_step)
            action_step.init_models(
                game=self.game, user=self.user, player=self.player,
                players=self.players,
            )
            action_step.check_parameters(**data)

        for action_step in self.steps:
            apply_condition = action_step.apply_condition(**data)
            if apply_condition:
                action_step.action(pipe, **data)
            else:
                action_step.otherwise(pipe, **data)

        pipe.execute()

        notify_game_players(self.game.id)

    def _init_models(self, user_id):
        self.user = User.get_by_id(redis, user_id, [User.current_game_id])
        self.player = Player.get_by_id(redis, user_id, [])
        game_id = self.user.current_game_id
        self.game = Game.get_by_id(redis, game_id, [Game.user_ids])

        self.players = [
            Player.get_by_id(redis, uid, []) for uid in self.game.user_ids
        ]

    def _update_models(self, action_step):
        self.game.fetch_fields(redis, action_step.game_fields)
        self.user.fetch_fields(redis, action_step.user_fields)
        self.player.fetch_fields(redis, action_step.player_fields)
        for player in self.players:
            player.fetch_fields(redis, action_step.all_player_fields)


class BaseStep:
    game_fields = []
    user_fields = []
    player_fields = []
    all_player_fields = []

    def init_models(self, **kwargs):
        self.game = kwargs.get('game')
        self.user = kwargs.get('user')
        self.player = kwargs.get('player')
        self.players = kwargs.get('players')

    @property
    def map_config(self):
        return config.config.maps.get(self.game.map)

    def check_parameters(self, *args, **kwargs):
        pass

    def apply_condition(self, *args, **kwargs):
        return True

    def action(self, pipe, *args, **kwargs):
        pass

    def otherwise(self, pipe, *args, **kwargs):
        pass


class TurnCheckStep(BaseStep):
    game_fields = [Game.turn, Game.step]

    def check_parameters(self, *args, **kwargs):
        if self.game.turn != self.user.id:
            raise EnergynetException('Its not your move')
        if self.game.step != self.step_type:
            raise EnergynetException('Step is not {}'.format(self.step_type))


class NextTurnStep(BaseStep):
    game_fields = [Game.step, Game.turn, Game.order]

    def __init__(self, next_step_type):
        self.next_step_type = next_step_type

    def action(self, pipe, *args, **kwargs):
        index = self.game.order.index(self.player.id)
        if index <= 0:
            Game.turn.write(pipe, self.game.order[-1], self.game.id)
            Game.step.write(pipe, self.next_step_type, self.game.id)
        else:
            Game.turn.write(pipe, self.game.order[index - 1], self.game.id)
