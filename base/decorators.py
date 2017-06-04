from flask_socketio import emit

from utils.server import app
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
                app.logger.error('TransactionFailed')
                emit(topic, {
                    'success': False,
                    'message': 'Failed to execute transaction'
                })
            except Exception as e:
                app.logger.error('Response error', exception=e)
                emit(topic, {
                    'success': False,
                    'message': 'Unknown exception'
                })

        return wrapper
    return _game_response
