from flask_socketio import emit, join_room

# from games.models import Game, GamesList


def create_new(data):
    name = data['name']
    players_limit = data['playersLimit']

    games_list = GamesList()
    id = games_list.get_new_id()
    game = Game({
        'id': id,
        'name': name,
        'playersLimit': players_limit,
        'started': False,
    })
    games_list.add(game)

    key = 'game:%d' % game.data.get('id')
    join_room(key)

    games = games_list.get_all()
    emit('new', {
        'success': True,
    })
    emit(
        'games', [game.data for game in games], namespace='/games',
        broadcast=True
    )
