from unittest.mock import patch
from test.base import BaseTest

from utils.server import app
from utils.socket_server import io
from utils.redis import redis

from core.models import Game, User, Lobby


class JoinTestCase(BaseTest):
    def setUp(self):
        self.user = self.create_user(name='user')

        self.game = Game()
        self.game.id = self.user.id + 1
        self.game.data = {'name': 'game_1'}
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
        self.assertRedisInt(self.lobby.id, 'user:%d:current_lobby_id' % self.user.id)
        self.assertRedisListInt([self.user.id], 'game:%s:user_ids' % self.game.id)

    @patch('flask_login._get_user')
    def test_join_second_user(self, load_user_mock):
        self.game.user_ids = [self.user.id]
        self.game.save()

        user_1 = User()
        user_1.id = self.user.id
        user_1.current_lobby_id = self.lobby.id
        user_1.save()

        self.user_2 = self.create_user(name='user_2')
        load_user_mock.return_value = self.user_2
        self.client = io.test_client(app)
        self.client.get_received()

        self.client.emit('join', {'id': self.game.id})

        received = self.client.get_received()

        self.client.disconnect()
        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertRedisInt(self.lobby.id, 'user:%d:current_lobby_id' % self.user.id)
        self.assertRedisInt(self.lobby.id, 'user:%d:current_lobby_id' % self.user_2.id)
        self.assertRedisListInt([self.user.id, self.user_2.id], 'game:%s:user_ids' % self.game.id)

        User.get_by_id(self.user_2.id).delete()
