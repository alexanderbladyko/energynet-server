from flask_socketio import join_room, leave_room

from core.models import User
from utils.redis import redis, redis_retry_transaction


def ensure_user(db_user):
    if redis.sismember(User.key, db_user.id):
        return User.get_by_id(db_user.id)
    else:
        pipe = redis.pipeline()
        return _create_user(pipe, db_user)


@redis_retry_transaction()
def _create_user(pipe, db_user):
    pipe.watch(User.key)

    instance = User()
    instance.id = db_user.id
    instance.data = {
        'name': db_user.name,
    }

    pipe.hmset(User.data.key(instance.id), instance.data)
    pipe.execute()

    return instance


def join_game(game_id):
    join_room('games:%s' % game_id)


def leave_game(game_id):
    leave_room('games:%s' % game_id)
