from flask_socketio import join_room, emit
from flask_login import current_user

from games.models import GamesList, GameUser
from auth.helpers import authenticated_only


@authenticated_only
def join_lobby(data):
    id = data['id']

    games_list = GamesList()
    game = games_list.get_by_id(id)

    if not game:
        return

    users_list = game.get_users()
    game_user = GameUser({
        'id': current_user.id,
        'name': current_user.name,
    })
    users_list.add(game_user)
    game_user.save_game_id(id)

    room_key = 'games:%s' % id
    join_room(room_key)

    lobby_info = game.data.copy()
    lobby_info.update({
        'users': [user.data for user in users_list.get_all()]
    })

    emit('join_game', {
        'success': True,
    })
    emit('lobby', lobby_info, room=room_key)
