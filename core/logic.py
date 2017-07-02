from flask_socketio import join_room, leave_room

from auth.models import User as DbUser
from core.models import User
from utils.redis import redis, redis_retry_transaction


def ensure_user(user_id):
    if redis.exists(User.data.key(user_id)):
        return User.get_by_id(redis, user_id)
    else:
        pipe = redis.pipeline()
        db_user = DbUser.get_by_id(user_id, [
            DbUser.Fields.ID, DbUser.Fields.NAME
        ])
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


def game_room_key(game_id):
    return 'games:%s' % game_id


def join_game(game_id):
    join_room(game_room_key(game_id))


def leave_game(game_id):
    leave_room(game_room_key(game_id))
