from flask_socketio import emit, join_room
from flask_login import current_user

from auth.helpers import authenticated_only
from games.models import User, Game, Lobby
from utils.redis import redis
from utils.server import app


@authenticated_only
def create_new(data):
    name = data['name']
    players_limit = data['playersLimit']

    app.logger.info(
        'New game creating (%s, %s)' % (name, players_limit)
    )

    user = User.get_by_id(current_user.id)
    if user.current_lobby_id or user.current_game_id:
        emit('new', {
            'success': False,
            'message': 'User is already in the game'
        })
        return

    pipeline = redis.pipeline()

    game = Game()
    game.data = {
        'name': name,
        'players_limit': players_limit,
    }
    game.owner_id = current_user.id
    game.user_ids = [current_user.id]
    game.save(p=pipeline)

    lobby = Lobby()
    lobby.id = game.id
    lobby.save(p=pipeline)

    user.current_lobby_id = lobby.id
    user.save(p=pipeline)

    pipeline.execute()

    games = Game.get_all()

    key = 'game:%d' % game.id
    join_room(key)

    emit('new_game', {
        'success': True,
    })
    emit(
        'games', [game.serialize() for game in games],
        namespace='/games', broadcast=True
    )
