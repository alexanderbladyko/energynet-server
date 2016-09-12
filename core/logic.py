from flask_socketio import join_room, leave_room

from core.models import User
from utils.redis import redis


def ensure_user(db_user, p=None):
    if not redis.sismember(User.key, db_user.id):
        pipeline = p if p is not None else redis.pipeline()

        user = User()
        user.id = db_user.id
        user.data = {
            'name': db_user.name,
        }
        user.save(p)

        if p is None:
            pipeline.execute()

        return user
    else:
        return User.get_by_id(db_user.id)


def join_game(game_id):
    join_room('games:%s' % game_id)


def leave_game(game_id):
    leave_room('games:%s' % game_id)
