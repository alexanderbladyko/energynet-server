from flask import jsonify

from utils.config import config


def get_config():
    host = config.get('app', 'host')
    port = config.get('app', 'port')
    game_api = config.get('urls', 'game_api')
    auth_api = config.get('urls', 'auth_api')
    return jsonify({
        'serverUrl': '%s:%s' % (host, port),
        'gameApi': game_api,
        'authApi': auth_api,
    })
