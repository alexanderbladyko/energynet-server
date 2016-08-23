from flask_login import current_user

from games.models import Game, User


class UserState:
    class USER_STATUSES:
        USER_IN_GAME = 'USER_IN_GAME'
        USER_IN_LOBBY = 'USER_IN_LOBBY'
        USER_NOT_INVOLVED = 'USER_NOT_INVOLVED'

    def get_status(self):
        user = User.get_by_id(current_user.id, [
            User.current_game_id, User.current_lobby_id
        ])

        game_id = user.current_game_id
        if game_id:
            game = Game.get_by_id(game_id)
            if game.data['started'] == 'True':
                return UserState.USER_STATUSES.USER_IN_GAME
            else:
                return UserState.USER_STATUSES.USER_IN_LOBBY
        else:
            return UserState.USER_STATUSES.USER_NOT_INVOLVED
