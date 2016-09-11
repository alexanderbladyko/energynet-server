from flask import jsonify

from utils.config import config


def get_config():
    game_api = config.get('urls', 'game_api')
    auth_api = config.get('urls', 'auth_api')
    return jsonify({
        'gameApi': game_api,
        'authApi': auth_api,
    })
