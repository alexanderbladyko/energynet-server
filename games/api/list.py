from flask_socketio import emit

from auth.helpers import authenticated_only
from games.logic import get_lobbies
from utils.server import app


@authenticated_only
def get_list():
    app.logger.info(
        'Games list'
    )

    emit('games', get_lobbies())
