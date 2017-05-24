from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser
from core.logic import ensure_user
from utils.server import app
from utils.socket_server import io
from utils.redis import redis

from core.models import Game, User, Lobby

from test import factories


class StartGameTestCase(BaseTest):
    def setUp(self):
        self.user = self.create_user(name='user')
        self.game = factories.GameFactory.create(
            data={'name': 'game1', 'players_limit': 3}, owner_id=self.user.id,
        )

        self.lobby = factories.LobbyFactory.create(self.game.id)

        self.user_1 = ensure_user(self.user)
        User.current_game_id.write(redis, self.game.id, self.user_1.id)
        User.current_lobby_id.write(redis, self.game.id, self.user_1.id)
        self.user_2 = factories.UserFactory.create(
            data={'name': 'user_2'}, current_game_id=self.game.id,
            current_lobby_id=self.game.id,
        )
        self.user_3 = factories.UserFactory.create(
            data={'name': 'user_3'}, current_game_id=self.game.id,
            current_lobby_id=self.game.id,
        )
        Game.user_ids.write(
            redis, {self.user_1.id, self.user_2.id, self.user_3.id},
            self.game.id
        )

        super(StartGameTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        self.game.remove(redis)
        User.delete(redis, self.user.id)
        User.delete(redis, self.user_2.id)
        User.delete(redis, self.user_3.id)

        redis.delete(User.key)
        redis.delete(Lobby.key)
        redis.delete(Game.key)

        redis.delete(Game.index())
        redis.delete(User.index())

        super(StartGameTestCase, self).tearDown()

    def test_start(self):
        with patch('games.logic.emit') as emit_mock:
            with patch('flask_login._get_user') as load_user_mock:
                load_user_mock.return_value = self.user
                self.client = io.test_client(app)
                self.client.get_received()

                self.client.emit('start', {})

                received = self.client.get_received()

                self.client.disconnect()

        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertRedisInt(
            self.lobby.id, User.current_lobby_id.key(self.user.id)
        )
        self.assertEqual(
            Game.user_ids.read(redis, self.game.id),
            {self.user_1.id, self.user_2.id, self.user_3.id},
        )
        self.assertFalse(redis.sismember(Lobby.key, self.game.id))
