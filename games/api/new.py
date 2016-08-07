from flask_socketio import emit, join_room

from games.models import Game


def create_new(data):
    name = data['name']
    players_limit = data['playersLimit']

    game = Game.add(name, players_limit)

    key = 'game:%d' % game.data.get('id')
    join_room(key)

    games = Game.get_all()
    emit('new', {
        'success': True,
    })
    emit('games', games, namespace='/games', broadcast=True)
