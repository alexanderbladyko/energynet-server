from auth.routes import AuthRoutes
from core.routes import CoreRoutes

routes = [
    AuthRoutes(),
    CoreRoutes(),
]


def init_routes():
    for instance in routes:
        instance.init_routes()
