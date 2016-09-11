from unittest.mock import patch
from test.base import BaseTest

from core.logic import ensure_user
from core.models import Game, User, Lobby
from utils.server import app
from utils.socket_server import io
from utils.redis import redis


class LeaveTestCase(BaseTest):
    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        self.user = self.create_user(self.username, self.password)
        self.user_1 = ensure_user(self.user)

        self.game = Game()
        self.game.id = self.user.id + 1
        self.game.user_ids = [self.user.id]
        self.game.data = {'name': 'game_1'}
        self.game.save()

        self.lobby = Lobby()
        self.lobby.id = self.game.id
        self.lobby.save()

        super(LeaveTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute('delete from public.user *;')
            self.db.commit()

        self.user_1.delete()
        self.lobby.delete()
        self.game.delete()
        redis.delete('game:index')
        redis.delete('user:index')

        super(LeaveTestCase, self).tearDown()

    @patch('flask_login._get_user')
    def test_leave(self, load_user_mock):
        load_user_mock.return_value = self.user
        self.client = io.test_client(app)
        redis.set('user:%s:current_lobby_id' % self.user.id, self.lobby.id)
        self.client.get_received()

        self.client.emit('leave', {})

        received = self.client.get_received()

        self.client.disconnect()
        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertRedisListInt([], 'game:%s:user_ids' % self.game.id)

    @patch('flask_login._get_user')
    def test_leave_two_users(self, load_user_mock):
        user = self.create_user(name='user_2')
        user_2 = ensure_user(user)

        load_user_mock.return_value = user

        self.game.user_ids = [self.user_1.id, user_2.id]
        self.game.save()

        self.client = io.test_client(app)
        redis.set('user:%s:current_lobby_id' % user_2.id, self.lobby.id)
        self.client.get_received()

        self.client.emit('leave', {})

        received = self.client.get_received()

        self.client.disconnect()
        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertRedisListInt([self.user.id], 'game:%s:user_ids' % self.game.id)

        user_2.delete()
