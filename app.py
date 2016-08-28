from gevent import monkey

from utils.config import config
from utils.logger import handler
from utils.server import app
from utils.socket_server import io
from utils.login_manager import init_login_manager

from routes import init_routes
from tasks import init_tasks

monkey.patch_all()

init_login_manager()
init_routes()
init_tasks()

app.logger.addHandler(handler)

if __name__ == '__main__':
    port = int(config.get('app', 'port'))

    print('Running at port: %s' % port)
    io.run(app, '0.0.0.0', port=port)
