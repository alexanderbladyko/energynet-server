from auth.routes import AuthRoutes
from core.routes import CoreRoutes
from games.routes import GamesRoutes

routes = [
    AuthRoutes(),
    CoreRoutes(),
    GamesRoutes(),
]


def init_routes():
    for instance in routes:
        instance.init_routes()
