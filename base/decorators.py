from flask_socketio import emit

from base.exceptions import EnergynetException
from utils.redis import (
    RedisTransactionException
)

import structlog
logger = structlog.get_logger()


def game_response(topic):
    def _game_response(fn):
        def wrapper(data, *args, **kwargs):
            try:
                response = fn(data, *args, **kwargs)
                if response:
                    emit(topic, response)
            except EnergynetException as e:
                logger.error('APIError', exception=e)
                emit(topic, {
                    'success': False,
                    'message': e.message
                })
            except RedisTransactionException:
                logger.error('TransactionFailed')
                emit(topic, {
                    'success': False,
                    'message': 'Failed to execute transaction'
                })
            except Exception as e:
                logger.error('ResponseError', exception=e)
                emit(topic, {
                    'success': False,
                    'message': 'Unknown exception'
                })

        return wrapper
    return _game_response
