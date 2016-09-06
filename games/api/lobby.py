from flask_socketio import emit, join_room
from flask_login import current_user

from core.models import Game, User


def get_lobby(data):

    user = User.get_by_id(current_user.id, [User.current_lobby_id])
    if not user.current_lobby_id:
        return

    game = Game.get_by_id(user.current_lobby_id, [
        Game.user_ids,
        Game.data,
    ])

    lobby_info = game.data.copy()
    users = User.get_all([User.data, User.game_data])
    lobby_info.update({
        'users': [user.serialize() for user in users]
    })

    room_key = 'games:%s' % id
    join_room(room_key)
    emit('lobby', lobby_info, room=room_key)
