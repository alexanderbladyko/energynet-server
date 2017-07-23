from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser
from core.models import Game, User, Player

from utils.redis import redis

from test import factories


class AuctionInfoTestCase(BaseTest):
    def setUp(self):
        self.db_user_1 = self.create_user(name='user_1')
        self.db_user_2 = self.create_user(name='user_2')
        self.db_user_3 = self.create_user(name='user_3')

        self.game = factories.GameFactory.create(
            data={'name': 'game1', 'players_limit': 3},
            owner_id=self.db_user_1.id, map=self.map,
            user_ids={self.db_user_1.id, self.db_user_2.id, self.db_user_3.id}
        )

        self.user_1 = factories.UserFactory.ensure_from_db(
            self.db_user_1, current_game_id=self.game.id,
            current_lobby_id=self.game.id
        )
        self.user_2 = factories.UserFactory.ensure_from_db(
            self.db_user_2, current_game_id=self.game.id,
            current_lobby_id=self.game.id
        )
        self.user_3 = factories.UserFactory.ensure_from_db(
            self.db_user_3, current_game_id=self.game.id,
            current_lobby_id=self.game.id
        )
        self.user_ids = [self.user_1.id, self.user_2.id, self.user_3.id]

        super().setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        self.game.remove(redis)
        User.delete(redis, self.user_1.id)
        User.delete(redis, self.user_2.id)
        User.delete(redis, self.user_3.id)
        Player.delete(redis, self.user_1.id)
        Player.delete(redis, self.user_2.id)
        Player.delete(redis, self.user_3.id)

        redis.delete(User.key)
        redis.delete(Game.key)

        redis.delete(Game.index())
        redis.delete(User.index())

        super().tearDown()

    def test_auction(self):
        stations = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        Game.stations.write(redis, stations, self.game.id)

        with self.user_logged_in(self.db_user_1.id):
            with patch('config.config', self.map_config_mock):
                client = self.create_test_client()
                client.get_received()

                client.emit('auction', {})
                received = client.get_received()

                client.disconnect()

        data = received[0]['args'][0]
        self.assertEqual(data['meta'], {
            'left': 7,
        })
        self.assertEqual(data['data'], [
            {'available': True, 'cost': 1.0},
            {'available': True, 'cost': 2.0},
            {'available': True, 'cost': 3.0},
            {'available': False, 'cost': 4.0},
            {'available': False, 'cost': 5.0},
            {'available': False, 'cost': 6.0},
        ])
