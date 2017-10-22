from flask_socketio import emit

from auth.helpers import authenticated_only
from core.logic import join_game
from core.models import User
from game.logic import get_game_data
from utils.redis import redis


@authenticated_only
def game_info(user_id, data):
    user = User.get_by_id(redis, user_id, [User.current_game_id])

    game_id = user.current_game_id

    join_game(game_id)
    emit('game', get_game_data(game_id))
