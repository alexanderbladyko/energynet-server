from auth.helpers import authenticated_only
from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game, User, Player
from game.logic import notify_game_players
from utils.redis import redis, redis_retry_transaction


@authenticated_only
def station_remove(user_id, data):
    station = data.get('station')

    pipe = redis.pipeline()
    station_remove_transaction(pipe, user_id, station)

    return {'success': True}


@redis_retry_transaction()
def station_remove_transaction(pipe, user_id, station):
    user = User.get_by_id(redis, user_id, [User.current_game_id])
    game_id = user.current_game_id

    pipe.watch(Game.auction.key(game_id))
    pipe.watch(Game.auction_user_ids.key(game_id))
    pipe.watch(Game.step.key(game_id))
    pipe.watch(Game.turn.key(game_id))
    pipe.watch(Player.stations.key(user_id))

    player = Player.get_by_id(redis, user_id, [Player.stations])

    if station not in player.stations:
        raise EnergynetException('Invalid station')

    game = Game.get_by_id(redis, game_id, [
        Game.map, Game.turn, Game.step, Game.user_ids, Game.order,
        Game.auction_user_ids, Game.auction_passed_user_ids,
    ])

    if game.turn != user_id:
        raise EnergynetException('Its not your move')
    if game.step != StepTypes.STATION_REMOVE:
        raise EnergynetException('Its not STATION_REMOVE')

    pipe.srem(Player.stations.key(user_id), station)
    if game.get_users_left_for_auction() == {user_id}:
        Game.step.write(pipe, StepTypes.RESOURCES_BUY, game.id)
        Game.turn.write(pipe, game.order[-1], game.id)
        Game.auction_user_ids.delete(pipe, game.id)
    else:
        Game.step.write(pipe, StepTypes.AUCTION, game.id)
        next_user_id = game.get_next_user_id(
            user.id, exclude_ids=game.auction_user_ids
        )
        Game.turn.write(pipe, next_user_id, game.id)

    pipe.execute()

    notify_game_players(game.id)
