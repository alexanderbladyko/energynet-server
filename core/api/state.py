from flask_socketio import emit

from core.logic import UserState


def get_state(data):
    user_state = UserState()
    status = user_state.get_status()

    if status == UserState.USER_STATUSES.USER_NOT_INVOLVED:
        emit('state', {
            'inGame': False
        })
    elif status == UserState.USER_STATUSES.USER_IN_LOBBY:
        emit('state', {
            'inGame': True,
            'inLobby': True,
        })
    elif status == UserState.USER_STATUSES.USER_IN_GAME:
        emit('state', {
            'inGame': True,
            'inLobby': False,
        })
