from flask_socketio import emit

from core.models import Game, User


def notify_lobby_users(game_id=None, game=None):
    if not game:
        game = Game.get_by_id(game_id, [
            Game.user_ids,
            Game.data,
        ])

    lobby_info = game.data.copy()
    users = User.get_by_ids(game.user_ids, [User.data, User.game_data])
    lobby_info.update({
        'users': [user.serialize() for user in users]
    })

    room_key = 'games:%s' % game.id
    emit('lobby', lobby_info, room=room_key)
