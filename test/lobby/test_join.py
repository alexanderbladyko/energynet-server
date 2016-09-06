from unittest.mock import patch
from test.base import BaseTest

from utils.server import app
from utils.socket_server import io
from utils.redis import redis

from core.models import Game, User, Lobby


class JoinTestCase(BaseTest):
    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        self.user = self.create_user(self.username, self.password)

        self.game = Game()
        self.game.id = self.user.id + 1
        self.game.save()

        self.lobby = Lobby()
        self.lobby.id = self.game.id
        self.lobby.save()

        super(JoinTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute('delete from public.user *;')
            self.db.commit()

        self.lobby.delete()
        self.game.delete()
        User.get_by_id(self.user.id).delete()
        redis.delete('game:index')
        redis.delete('user:index')

        super(JoinTestCase, self).tearDown()

    @patch('flask_login._get_user')
    def test_join(self, load_user_mock):
        load_user_mock.return_value = self.user
        self.client = io.test_client(app)
        self.client.get_received()

        self.client.emit('join', {'id': self.game.id})

        received = self.client.get_received()

        self.client.disconnect()
        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertEqual(bytes(str(self.lobby.id), 'utf-8'), redis.get('user:%s:current_lobby_id' % self.user.id))
        self.assertListEqual([bytes(str(self.user.id), 'utf-8')], redis.lrange('game:%s:user_ids' % self.game.id, 0, -1))
