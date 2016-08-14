from flask_login import current_user

from games.models import GameUser, GamesList


class UserState:
    class USER_STATUSES:
        USER_IN_GAME = 'USER_IN_GAME'
        USER_IN_LOBBY = 'USER_IN_LOBBY'
        USER_NOT_INVOLVED = 'USER_NOT_INVOLVED'

    def get_status(self):
        game_user = GameUser({
            'id': current_user.id,
        })
        game_id = game_user.get_game_id()
        if game_id:
            game = GamesList().get_by_id(game_id)
            if game.data['started'] == 'True':
                return UserState.USER_STATUSES.USER_IN_GAME
            else:
                return UserState.USER_STATUSES.USER_IN_LOBBY
        else:
            return UserState.USER_STATUSES.USER_NOT_INVOLVED
