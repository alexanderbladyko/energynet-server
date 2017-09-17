from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser
from core.constants import StepTypes
from core.models import Game, User, Player

from utils.redis import redis

from test import factories


class StationRemoveTestCase(BaseTest):
    def setUp(self):
        self.db_user_1 = self.create_user(name='user_1')
        self.db_user_2 = self.create_user(name='user_2')
        self.db_user_3 = self.create_user(name='user_3')

        self.stations = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0]

        self.game = factories.GameFactory.create(
            data={'name': 'game1', 'players_limit': 3},
            turn=self.db_user_1.id,
            owner_id=self.db_user_1.id,
            map=self.map,
            stations=self.stations,
            user_ids={self.db_user_1.id, self.db_user_2.id, self.db_user_3.id},
            order=[self.db_user_1.id, self.db_user_2.id, self.db_user_3.id],
            step=StepTypes.STATION_REMOVE,
            auction={},
            auction_user_ids={self.db_user_2.id, self.db_user_3.id},
        )

        self.user_1 = factories.UserFactory.ensure_from_db(
            self.db_user_1, current_game_id=self.game.id,
            current_lobby_id=self.game.id
        )
        Player.stations.write(redis, {2.0, 4.0, 5.0, 6.0}, self.user_1.id)
        self.user_2 = factories.UserFactory.ensure_from_db(
            self.db_user_2, current_game_id=self.game.id,
            current_lobby_id=self.game.id
        )
        self.user_3 = factories.UserFactory.ensure_from_db(
            self.db_user_3, current_game_id=self.game.id,
            current_lobby_id=self.game.id
        )
        self.user_ids = [self.user_1.id, self.user_2.id, self.user_3.id]

        self.notify_patcher = patch(
            'game.api.stations.notify_game_players'
        )
        self.map_config_patcher = patch('config.config', self.map_config_mock)

        self.notify_mock = self.notify_patcher.start()
        self.map_config_mock = self.map_config_patcher.start()

        super().setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        self.game.remove(redis)
        for user_id in self.user_ids:
            User.delete(redis, user_id)
            Player.delete(redis, user_id)

        redis.delete(User.key)
        redis.delete(Game.key)

        redis.delete(Game.index())
        redis.delete(User.index())

        for patcher in [self.notify_patcher, self.map_config_patcher]:
            patcher.stop()

        super().tearDown()

    def _send_remove_station(self, data):
        client = self.create_test_client()
        client.get_received()

        client.emit('station_remove', data)
        received = client.get_received()
        client.disconnect()

        return received

    def test_station_remove(self):
        with self.user_logged_in(self.db_user_1.id):
            received = self._send_remove_station({
                'station': 4.0,
            })

        self.notify_mock.assert_called_with(self.game.id)

        game = Game.get_by_id(redis, self.game.id)
        self.assertEqual(game.auction, {
            'bid': None,
            'station': None,
            'user_id': None,
        })
        self.assertEqual(game.turn, self.user_3.id)
        self.assertEqual(game.auction_user_ids, set())
        self.assertEqual(game.step, StepTypes.RESOURCES_BUY)

        player = Player.get_by_id(redis, self.user_1.id)
        self.assertEqual(player.stations, {2.0, 5.0, 6.0})

        data = received[0]['args'][0]
        self.assertEqual(data, {'success': True})

    def test_station_remove_return_back_to_auction(self):
        Game.auction_user_ids.delete(redis, self.game.id)

        with self.user_logged_in(self.db_user_1.id):
            received = self._send_remove_station({
                'station': 4.0,
            })

        self.notify_mock.assert_called_with(self.game.id)

        game = Game.get_by_id(redis, self.game.id)
        self.assertEqual(game.auction, {
            'bid': None,
            'station': None,
            'user_id': None,
        })
        self.assertEqual(game.auction_user_ids, set())
        self.assertEqual(game.step, StepTypes.AUCTION)
        self.assertEqual(game.turn, self.user_2.id)

        player = Player.get_by_id(redis, self.user_1.id)
        self.assertEqual(player.stations, {2.0, 5.0, 6.0})

        data = received[0]['args'][0]
        self.assertEqual(data, {'success': True})

    def test_invalid_station(self):
        with self.user_logged_in(self.db_user_1.id):
            received = self._send_remove_station({
                'station': 3.0,
            })

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_not_your_turn(self):
        Player.stations.write(redis, {2.0, 4.0, 5.0, 6.0}, self.user_2.id)
        Game.turn.write(redis, self.user_2.id, self.game.id)
        with self.user_logged_in(self.user_1.id):
            received = self._send_remove_station({
                'station': 4.0,
            })

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_incorrect_step(self):
        Game.step.write(redis, StepTypes.AUCTION, self.game.id)
        with self.user_logged_in(self.user_1.id):
            received = self._send_remove_station({
                'station': 4.0,
            })

        data = received[0]['args'][0]
        self.assertFalse(data['success'])
