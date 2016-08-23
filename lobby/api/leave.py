from flask_socketio import leave_room, emit
from flask_login import current_user

# from games.models import GamesList, GameUser
from auth.helpers import authenticated_only
from base.exceptions import EnergynetException


@authenticated_only
def leave_lobby(data):
    game_user = GameUser({
        'id': current_user.id,
    })

    id = game_user.get_game_id()
    if not id:
        raise EnergynetException('User is not in game')

    games_list = GamesList()
    game = games_list.get_by_id(id)

    if not game:
        raise EnergynetException('User game not found: %s' % str(id))

    users_list = game.get_users()
    game_user = users_list.get_by_id(current_user.id)
    if not game_user:
        raise EnergynetException('User is not in the game: %s' % str(id))

    users_list.remove(current_user.id)
    game_user.remove_game_id()

    room_key = 'games:%s' % id
    leave_room(room_key)

    emit('leave_game', {
        'success': True,
    })
