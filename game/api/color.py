import config
from auth.helpers import authenticated_only
from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import User, Game, Player
from game.logic import notify_game_players
from utils.redis import redis, redis_retry_transaction


@authenticated_only
def choose_color(user_id, data):
    color = data.get('color')

    user = User.get_by_id(redis, user_id, [User.current_game_id])
    game_id = user.current_game_id
    game_map = Game.map.read(redis, game_id)

    map_config = config.config.maps.get(game_map)
    if color not in map_config.get('colors'):
        raise EnergynetException(message='Color is invalid')

    pipe = redis.pipeline()
    choose_color_transaction(pipe, game_id, user_id, color)

    notify_game_players(game_id)

    return {
        'success': True,
    }


@redis_retry_transaction()
def choose_color_transaction(pipe, game_id, user_id, color):
    pipe.watch(Game.reserved_colors.key(game_id))
    pipe.watch(Player.color.key(user_id))
    pipe.watch(Game.step.key(game_id))

    if pipe.get(Player.color.key(user_id)) is not None:
        pipe.unwatch()
        raise EnergynetException(message='Player has color')

    if pipe.sismember(Game.reserved_colors.key(game_id), color):
        pipe.unwatch()
        raise EnergynetException(message='Color is taken')

    pipe.sadd(Game.reserved_colors.key(game_id), color)
    pipe.set(Player.color.key(user_id), color)

    users_count = pipe.scard(Game.user_ids.key(game_id))
    colors_count = pipe.scard(Game.reserved_colors.key(game_id))
    if colors_count == users_count:
        Game.step.write(pipe, StepTypes.AUCTION, game_id)

    pipe.execute()
