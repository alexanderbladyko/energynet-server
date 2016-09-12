from flask_socketio import emit
from flask_login import current_user

from auth.helpers import authenticated_only
from core.logic import join_game
from core.models import User, Game, Lobby
from games.logic import notify_lobby_users
from utils.redis import redis_session
from utils.server import app


@authenticated_only
def join_lobby(data):
    app.logger.info(
        'Join lobby'
    )
    id = data['id']

    user = User.get_by_id(current_user.id)

    if user.current_lobby_id or user.current_game_id:
        emit('join_game', {
            'success': False,
            'message': 'User is already in the game'
        })
        return

    lobby_exists = Lobby.contains(id)

    if not lobby_exists:
        emit('join_game', {
            'success': False,
            'message': 'No such game'
        })
        return

    game = Game.get_by_id(id, [Game.user_ids, Game.data])

    with redis_session() as pipeline:
        game.add_user(user.id)
        game.save(p=pipeline)

        user.current_lobby_id = id
        user.save(p=pipeline)

    join_game(id)

    emit('join_game', {
        'success': True,
    })
    notify_lobby_users(game=game)
