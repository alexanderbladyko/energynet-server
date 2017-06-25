from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser
from core.logic import ensure_user
from core.models import Game, Lobby, User

from utils.redis import redis

from test import factories


class LeaveTestCase(BaseTest):
    def setUp(self):
        self.username = 'test_user'
        self.user = self.create_user(name=self.username)

        self.user_1 = ensure_user(self.user.id)

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

    def test_leave(self):
        redis.set(User.current_lobby_id.key(self.user.id), self.lobby.id)
        with patch('games.logic.emit') as emit_mock:
            with patch('core.logic.leave_room') as leave_room_mock:
                with self.user_logged_in(self.user.id):
                    client = self.create_test_client()
                    client.get_received()

                    client.emit('game_leave', {})

                    received = client.get_received()

                    client.disconnect()

        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertEqual(Game.user_ids.read(redis, self.game.id), set())
        leave_room_mock.assert_called_once_with('games:%s' % self.game.id)

        emit_mock.assert_called_once_with(
            'game_lobby', {
                'name': 'game1',
                'users': [],
                'players': [],
                'players_limit': 4,
                'ownerId': None,
            }, room='games:%s' % self.game.id
        )

    def test_leave_two_users(self):
        user = self.create_user(name='user_2')
        user_2 = ensure_user(user.id)

        Game.user_ids.write(
            redis, [self.user_1.id, user_2.id], id=self.game.id
        )
        redis.set(User.current_lobby_id.key(user_2.id), self.lobby.id)

        with patch('games.logic.emit') as emit_mock:
            with patch('core.logic.leave_room') as leave_room_mock:
                with self.user_logged_in(user_2.id):
                    client = self.create_test_client()
                    client.get_received()

                    client.emit('game_leave', {})

                    received = client.get_received()

                    client.disconnect()

        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertEqual(
            Game.user_ids.read(redis, self.game.id), {self.user.id}
        )

        leave_room_mock.assert_called_once_with('games:%s' % self.game.id)

        emit_mock.assert_called_once_with(
            'game_lobby', {
                'name': 'game1',
                'users': [],
                'players': [{
                    'name': 'test_user',
                    'id': 2,
                }],
                'players_limit': 4,
                'ownerId': None,
            }, room='games:%s' % self.game.id
        )

        user_2.remove(redis)
