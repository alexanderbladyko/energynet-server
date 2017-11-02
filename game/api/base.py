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
        try:
            data = data or {}
            for action_step in self.steps:
                self._pipe_watch(pipe, action_step, **data)

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
        except EnergynetException:
            pipe.unwatch()
            raise

    def _pipe_watch(self, pipe, action_step, **kwargs):
        action_fields = (
            [f.key(self.game.id) for f in action_step.game_fields] +
            [f.key(self.user.id) for f in action_step.user_fields] +
            [f.key(self.player.id) for f in action_step.player_fields]
        )
        additional_keys = action_step.watch_keys(**kwargs)
        if additional_keys:
            action_fields += additional_keys
        if action_fields:
            pipe.watch(*action_fields)
        if action_step.all_player_fields:
            for player in self.players:
                pipe.watch(*(
                    [f.key(player.id) for f in action_step.all_player_fields]
                ))

    def _init_models(self, user_id):
        self.user = User.get_by_id(redis, user_id, [User.current_game_id])
        self.player = Player.get_by_id(redis, user_id, [])
        game_id = self.user.current_game_id
        self.game = Game.get_by_id(redis, game_id, [Game.user_ids])

        self.players = []
        for game_user_id in self.game.user_ids:
            if game_user_id == user_id:
                self.players.append(self.player)
            else:
                self.players.append(Player.get_by_id(redis, game_user_id, []))

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

    def watch_keys(self, *args, **kwargs):
        pass

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

    def __init__(self):
        self.check_turn = True

    def check_parameters(self, *args, **kwargs):
        if self.check_turn and self.game.turn != self.user.id:
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
            n_id = self.game.next_player_turn(reverse=True, from_start=True)
            Game.turn.write(pipe, n_id, self.game.id)
            Game.step.write(pipe, self.next_step_type, self.game.id)
        else:
            n_id = self.game.next_player_turn(reverse=True, from_start=False)
            Game.turn.write(pipe, n_id, self.game.id)
