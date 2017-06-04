from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser
from core.models import User
from utils.server import app
from utils.socket_server import io
from utils.redis import redis


class StateApiTestCase(BaseTest):
    def setUp(self):
        self.username = 'test_user'
        self.user = self.create_user(self.username)

        super(StateApiTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        User.delete(redis, self.user.id)

        redis.delete(User.index())

        super(StateApiTestCase, self).tearDown()

    @patch('flask_login.utils._get_user')
    def test_not_in_game(self, load_user_mock):
        load_user_mock.return_value = self.user

        self.client = io.test_client(app)
        # redis.set(User.current_lobby_id.key(self.user.id), self.lobby.id)
        self.client.get_received()

        self.client.emit('state', {})

        received = self.client.get_received()
        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{
            'inGame': False,
            'inLobby': False,
        }])


    @patch('flask_login.utils._get_user')
    def test_in_game_lobby(self, load_user_mock):
        load_user_mock.return_value = self.user

        self.client = io.test_client(app)
        redis.set(User.current_lobby_id.key(self.user.id), 10)
        redis.set(User.current_game_id.key(self.user.id), 10)
        self.client.get_received()

        self.client.emit('state', {})

        received = self.client.get_received()
        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{
            'inGame': True,
            'inLobby': True,
        }])
