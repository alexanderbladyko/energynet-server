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

        self.games_count = 4
        self.games = []
        for i in range(self.games_count):
            self.games.append(factories.GameFactory.create(
                data={'name': 'game_{}'.format(i), 'players_limit': i + 1}
            ))
        
        self.lobby_1 = factories.LobbyFactory.create(game_id=self.games[0].id)
        self.lobby_2 = factories.LobbyFactory.create(game_id=self.games[1].id)
        self.lobby_3 = factories.LobbyFactory.create(game_id=self.games[3].id)

        super(ListTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        self.user_1.remove(redis)
        self.lobby_1.remove(redis)
        self.lobby_2.remove(redis)
        self.lobby_3.remove(redis)
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
        redis.set(User.current_lobby_id.key(self.user.id), self.lobby.id)
        received = self.client.get_received()
        
        self.client.disconnect()
        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{
            'id': self.lobby_1,
            'name': self.games[0].name,
            'playersLimit': self.games[0].players_limit, 
        }, {
            'id': self.lobby_2,
            'name': self.games[1].name,
            'playersLimit': self.games[1].players_limit,            
        }, {
            'id': self.lobby_2,
            'name': self.games[3].name,
            'playersLimit': self.games[3].players_limit, 

        }])

