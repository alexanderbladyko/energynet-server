from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser
from core.logic import ensure_user
from core.models import Game, Lobby, User
from utils.server import app
from utils.socket_server import io
from utils.redis import redis

from test import factories


class ListTestCase(BaseTest):
    def setUp(self):
        self.username = 'test_user'
        self.user = self.create_user(name=self.username)

        self.user_1 = ensure_user(self.user)

        self.games = []
        for i in range(4):
            self.games.append(factories.GameFactory.create(
                data={'name': 'game_{}'.format(i), 'players_limit': i + 1}
            ))
        self.games_count = len(self.games)

        self.lobbies = []
        for i in [0, 1, 3]:
            game = self.games[i]
            self.lobbies.append(factories.LobbyFactory.create(game_id=game.id))

        super(ListTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        self.user_1.remove(redis)
        for lobby in self.lobbies:
            lobby.remove(redis)
        for game in self.games:
            game.remove(redis)

        redis.delete(Lobby.key)
        redis.delete(Game.key)

        redis.delete(Game.index())
        redis.delete(User.index())

        super(ListTestCase, self).tearDown()

    @patch('flask_login._get_user')
    def test_list(self, load_user_mock):
        load_user_mock.return_value = self.user
        self.client = io.test_client(app, namespace='/games')

        received = self.client.get_received('/games')

        self.client.disconnect()
        self.assertEqual(len(received), 1)
        asserted_list = received[0]['args'][0]

        expected_list = []
        for i in [0, 1, 3]:
            game = self.games[i]
            expected_list.append({
                'id': game.id,
                'name': game.data['name'],
                'playersLimit': game.data['players_limit'],
            })

        self.assertEqual(asserted_list, expected_list)
