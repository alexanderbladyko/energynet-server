from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser

from utils.server import app
from utils.socket_server import io
from utils.redis import redis

from core.models import Game, User, Lobby

from test import factories


class JoinTestCase(BaseTest):
    def setUp(self):
        self.user = self.create_user(name='user')

        self.game = factories.GameFactory.create(
            data={'name': 'game1', 'players_limit': 4}
        )
        self.lobby = factories.LobbyFactory.create(self.game.id)

        super(JoinTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        self.game.remove(redis)
        User.delete(redis, self.user.id)

        redis.delete(Lobby.key)
        redis.delete(Game.key)

        redis.delete(Game.index())
        redis.delete(User.index())

        super(JoinTestCase, self).tearDown()

    @patch('games.logic.emit')
    @patch('core.logic.join_room')
    @patch('flask_login.utils._get_user')
    def test_join(self, load_user_mock, join_room_mock, emit_mock):
        load_user_mock.return_value = self.user
        self.client = io.test_client(app)
        self.client.get_received()

        self.client.emit('join', {'id': self.game.id})

        received = self.client.get_received()

        self.client.disconnect()
        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertRedisInt(
            self.lobby.id, User.current_lobby_id.key(self.user.id)
        )
        self.assertEqual(
            Game.user_ids.read(redis, self.game.id), {self.user.id}
        )
        join_room_mock.assert_called_once_with('games:%s' % self.game.id)

        emit_mock.assert_called_once_with(
            'lobby', {
                'name': 'game1',
                'users': [{
                    'data': {'avatar': None, 'name': 'user'},
                    'id': 1
                }],
                'players_limit': 4
            }, room='games:%s' % self.game.id
        )

    @patch('games.logic.emit')
    @patch('core.logic.join_room')
    @patch('flask_login.utils._get_user')
    def test_join_second_user(self, load_user_mock, join_room_mock, emit_mock):
        Game.user_ids.write(redis, [self.user.id], id=self.game.id)

        User.current_lobby_id.write(redis, self.lobby.id, id=self.user.id)

        self.user_2 = self.create_user(name='user_2')
        load_user_mock.return_value = self.user_2
        self.client = io.test_client(app)
        self.client.get_received()

        self.client.emit('join', {'id': self.game.id})

        received = self.client.get_received()

        self.client.disconnect()
        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertRedisInt(
            self.lobby.id, User.current_lobby_id.key(self.user.id)
        )
        self.assertRedisInt(
            self.lobby.id, User.current_lobby_id.key(self.user_2.id)
        )
        self.assertEqual(
            Game.user_ids.read(redis, self.game.id),
            {self.user.id, self.user_2.id}
        )
        join_room_mock.assert_called_once_with('games:%s' % self.game.id)

        User.delete(redis, self.user_2.id)

        emit_mock.assert_called_once_with(
            'lobby', {
                'name': 'game1',
                'users': [{
                    'data': {'avatar': None, 'name': None},
                    'id': 2
                }, {
                    'data': {'avatar': None, 'name': 'user_2'},
                    'id': 3
                }],
                'players_limit': 4
            }, room='games:%s' % self.game.id
        )

    @patch('games.logic.emit')
    @patch('core.logic.join_room')
    @patch('flask_login.utils._get_user')
    def test_players_limit_exceeded(
            self, load_user_mock, join_room_mock, emit_mock
    ):
        Game.user_ids.write(redis, [self.user.id], id=self.game.id)
        redis.hset(Game.data.key(self.game.id), 'players_limit', 1)

        User.current_lobby_id.write(redis, self.lobby.id, id=self.user.id)

        self.user_2 = self.create_user(name='user_2')
        load_user_mock.return_value = self.user_2
        self.client = io.test_client(app)
        self.client.get_received()

        self.client.emit('join', {'id': self.game.id})

        received = self.client.get_received()

        self.client.disconnect()
        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{
            'success': False,
            'message': 'Players limit of game exceeded'
        }])
        self.assertRedisInt(
            self.lobby.id, User.current_lobby_id.key(self.user.id)
        )
        self.assertEqual(
            Game.user_ids.read(redis, self.game.id),
            {self.user.id}
        )
        join_room_mock.assert_not_called()

        User.delete(redis, self.user_2.id)

        emit_mock.assert_not_called()
