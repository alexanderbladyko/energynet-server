from flask_socketio import emit

from core.models import Game, User
from utils.redis import redis


def get_resources(user_id, data):
    user = User.get_by_id(redis, user_id, [User.current_game_id])

    game_id = user.current_game_id

    emit('resources', Game.resources.read(redis, game_id))
