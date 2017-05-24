from auth.routes import AuthRoutes
from core.routes import CoreRoutes
from game.routes import GameRoutes
from games.routes import GamesRoutes

routes = [
    AuthRoutes(),
    CoreRoutes(),
    GameRoutes(),
    GamesRoutes(),
]


def init_routes():
    for instance in routes:
        instance.init_routes()
