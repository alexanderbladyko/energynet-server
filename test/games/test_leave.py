from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser
from core.logic import ensure_user
from core.models import Game, Lobby, User
from utils.server import app
from utils.socket_server import io
from utils.redis import redis

from test import factories


class LeaveTestCase(BaseTest):
    def setUp(self):
        self.username = 'test_user'
        self.user = self.create_user(name=self.username)

        self.user_1 = ensure_user(self.user)

        self.game = factories.GameFactory.create(
            user_ids=[self.user.id], data={'name': 'game1', 'players_limit': 4}
        )
        self.lobby = factories.LobbyFactory.create(self.game.id)

        super(LeaveTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        self.user_1.remove(redis)
        self.lobby.remove(redis)
        self.game.remove(redis)

        redis.delete(Lobby.key)
        redis.delete(Game.key)

        redis.delete(Game.index())
        redis.delete(User.index())

        super(LeaveTestCase, self).tearDown()

    @patch('games.logic.emit')
    @patch('core.logic.leave_room')
    @patch('flask_login._get_user')
    def test_leave(self, load_user_mock, leave_room_mock, emit_mock):
        load_user_mock.return_value = self.user
        self.client = io.test_client(app)
        redis.set(User.current_lobby_id.key(self.user.id), self.lobby.id)
        self.client.get_received()

        self.client.emit('leave', {})

        received = self.client.get_received()

        self.client.disconnect()
        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertEqual(Game.user_ids.read(redis, self.game.id), set())
        leave_room_mock.assert_called_once_with('games:%s' % self.game.id)

        emit_mock.assert_called_once_with(
            'lobby', {
                'name': 'game1',
                'users': [],
                'players_limit': 4
            }, room='games:%s' % self.game.id
        )

    @patch('games.logic.emit')
    @patch('core.logic.leave_room')
    @patch('flask_login._get_user')
    def test_leave_two_users(self, load_user_mock, leave_room_mock, emit_mock):
        user = self.create_user(name='user_2')
        user_2 = ensure_user(user)

        load_user_mock.return_value = user

        Game.user_ids.write(
            redis, [self.user_1.id, user_2.id], id=self.game.id
        )

        self.client = io.test_client(app)
        redis.set(User.current_lobby_id.key(user_2.id), self.lobby.id)
        self.client.get_received()

        self.client.emit('leave', {})

        received = self.client.get_received()

        self.client.disconnect()
        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertEqual(
            Game.user_ids.read(redis, self.game.id), {self.user.id}
        )

        leave_room_mock.assert_called_once_with('games:%s' % self.game.id)

        emit_mock.assert_called_once_with(
            'lobby', {
                'name': 'game1',
                'users': [{
                    'data': {'avatar': None, 'name': 'test_user'},
                    'id': 2,
                    'game_data': {'color': None, 'money': None}
                }],
                'players_limit': 4
            }, room='games:%s' % self.game.id
        )

        user_2.remove(redis)
