from auth.routes import AuthRoutes
from core.routes import CoreRoutes
from games.routes import GamesRoutes
from lobby.routes import LobbyRoutes

routes = [
    AuthRoutes(),
    CoreRoutes(),
    GamesRoutes(),
    LobbyRoutes(),
]


def init_routes():
    for instance in routes:
        instance.init_routes()
