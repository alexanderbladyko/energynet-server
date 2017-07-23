from test.base import BaseTest

from auth.models import User as DbUser
from core.models import User

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

    def test_not_in_game(self):
        with self.user_logged_in(self.user.id):
            client = self.create_test_client()
            # redis.set(User.current_lobby_id.key(self.user.id), self.lobby.id)
            client.get_received()

            client.emit('state', {})

            received = client.get_received()
            client.disconnect()

        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{
            'inGame': False,
            'inLobby': False,
        }])

    def test_in_game_lobby(self):
        with self.user_logged_in(self.user.id):
            client = self.create_test_client()
            redis.set(User.current_lobby_id.key(self.user.id), 10)
            redis.set(User.current_game_id.key(self.user.id), 10)
            client.get_received()

            client.emit('state', {})

            received = client.get_received()
            client.disconnect()

        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{
            'inGame': True,
            'inLobby': True,
        }])
