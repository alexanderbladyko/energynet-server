from flask_socketio import emit

from base.exceptions import EnergynetException
from utils.redis import (
    RedisTransactionException
)


def game_response(topic):
    def _game_response(fn):
        def wrapper(data):
            try:
                response = fn(data)
                if response:
                    emit(topic, response)
            except EnergynetException as e:
                emit(topic, {
                    'success': False,
                    'message': e.message
                })
            except RedisTransactionException:
                emit(topic, {
                    'success': False,
                    'message': 'Failed to execute transaction'
                })
            except:
                emit(topic, {
                    'success': False,
                    'message': 'Unknown exception'
                })

        return wrapper
    return _game_response
