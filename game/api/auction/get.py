from flask_socketio import emit

import config

from auth.helpers import authenticated_only
from core.models import Game, User
from game.logic import get_auction_data
from utils.redis import redis


@authenticated_only
def get_auction(user_id, data):
    user = User.get_by_id(redis, user_id, [User.current_game_id])

    game_id = user.current_game_id

    game_map = Game.map.read(redis, game_id)

    map_config = config.config.maps.get(game_map)

    emit('auction', get_auction_data(game_id, map_config))
