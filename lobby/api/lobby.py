from flask_socketio import emit, join_room
from flask_login import current_user

# from games.models import GameUser, GamesList


def get_lobby(data):
    game_user = GameUser({
        'id': current_user.id,
        'name': current_user.name,
    })
    game_id = game_user.get_game_id()

    game = GamesList().get_by_id(game_id)

    users_list = game.get_users()
    lobby_info = game.data.copy()
    lobby_info.update({
        'users': [user.data for user in users_list.get_all()]
    })
    room_key = 'games:%s' % id
    join_room(room_key)
    emit('lobby', lobby_info, room=room_key)
