from flask import jsonify
from flask_login import current_user
from gevent import monkey

from utils.config import config
from utils.logger import handler
from utils.server import app
from utils.socket_server import io
from utils.login_manager import init_login_manager

from routes import init_routes
from tasks import init_tasks

monkey.patch_all()

game_api = config.get('urls', 'game_api')

init_login_manager()
init_routes()
init_tasks()


@app.route('{0}/user_info'.format(game_api))
def get_user_info():
    response = {}
    response['isAuthenticated'] = current_user.is_authenticated
    if current_user.is_authenticated:
        response['name'] = current_user.name

    return jsonify(response)

if __name__ == '__main__':
    port = int(config.get('app', 'port'))

    app.logger.addHandler(handler)
    print('Running at port: %s' % port)
    io.run(app, '0.0.0.0', port=port)
