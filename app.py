from utils.config import config
from utils.server import create_app, socketio

import routes  # noqa

app = create_app()

if __name__ == '__main__':
    port = int(config.get('socketio', 'port'))

    print('Running at port: %s' % port)
    socketio.run(app, '127.0.0.1', port=port)
