from auth.routes import AuthRoutes

routes = [
    AuthRoutes(),
]


def init_routes():
    for instance in routes:
        instance.init_routes()
