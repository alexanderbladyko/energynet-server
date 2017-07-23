from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser
from core.constants import StepTypes
from core.models import Game, User, Player

from utils.redis import redis

from test import factories


class AuctionPassTestCase(BaseTest):
    def setUp(self):
        self.db_user_1 = self.create_user(name='user_1')
        self.db_user_2 = self.create_user(name='user_2')
        self.db_user_3 = self.create_user(name='user_3')

        self.stations = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]

        self.initial_auction = {
            'bid': 4,
            'station': 5.0,
            'user_id': self.db_user_3.id,
        }
        self.game = factories.GameFactory.create(
            data={'name': 'game1', 'players_limit': 3},
            turn=self.db_user_1.id,
            owner_id=self.db_user_1.id,
            map=self.map,
            stations=self.stations,
            user_ids={self.db_user_1.id, self.db_user_2.id, self.db_user_3.id},
            order=[self.db_user_1.id, self.db_user_2.id, self.db_user_3.id],
            step=StepTypes.AUCTION,
            auction=self.initial_auction,
            phase=1,
            auction_passed_user_ids=[],
            auction_user_ids=[],
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

        self.notify_patcher = patch('game.api.auction.notify_game_players')
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

    def _create_auction_pass(self):
        client = self.create_test_client()
        client.get_received()

        client.emit('auction_pass', {})
        received = client.get_received()
        client.disconnect()

        return received

    def _check_game_is_not_changed(self):
        self.notify_mock.assert_not_called()

        auctionData = Game.auction.read(redis, self.game.id)
        self.assertEqual(auctionData, self.initial_auction)

    def test_not_your_turn(self):
        Game.turn.write(redis, self.user_2.id, self.game.id)
        with self.user_logged_in(self.user_1.id):
            received = self._create_auction_pass()

        self._check_game_is_not_changed()

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_auction_pass_with_no_passed(self):
        with self.user_logged_in(self.db_user_1.id):
            received = self._create_auction_pass()

        self.notify_mock.assert_called_with(self.game.id)

        game = Game.get_by_id(redis, self.game.id)

        self.assertEqual(game.auction, {
            'bid': 4,
            'station': 5.0,
            'user_id': self.user_3.id,
        })
        self.assertEqual(game.turn, self.user_2.id)
        self.assertEqual(game.auction_passed_user_ids, {self.user_1.id})

        data = received[0]['args'][0]
        self.assertEqual(data, {'success': True})

    def test_incorrect_step(self):
        Game.step.write(redis, StepTypes.STATION_REMOVE, self.game.id)
        with self.user_logged_in(self.user_1.id):
            received = self._create_auction_pass()

        self._check_game_is_not_changed()

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_cannot_pass_on_first_phase(self):
        Game.phase.write(redis, 0, self.game.id)
        Game.auction.delete(redis, self.game.id)
        with self.user_logged_in(self.user_1.id):
            received = self._create_auction_pass()

        self.notify_mock.assert_not_called()

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_pass_station(self):
        Game.auction.delete(redis, self.game.id)
        with self.user_logged_in(self.user_1.id):
            received = self._create_auction_pass()

        self.notify_mock.assert_called_with(self.game.id)

        game = Game.get_by_id(redis, self.game.id)
        self.assertEqual(game.turn, self.user_2.id)

        data = received[0]['args'][0]
        self.assertTrue(data['success'])

    def test_last_user_passed(self):
        Game.auction_passed_user_ids.write(redis, {
            self.user_2.id
        }, self.game.id)

        with self.user_logged_in(self.user_1.id):
            received = self._create_auction_pass()

        self.notify_mock.assert_called_with(self.game.id)

        game = Game.get_by_id(redis, self.game.id)
        self.assertEqual(game.auction, {
            'bid': None,
            'station': None,
            'user_id': None,
        })
        self.assertEqual(game.step, StepTypes.AUCTION)
        self.assertEqual(game.turn, self.user_1.id)

        user_stations = Player.stations.read(redis, self.user_3.id)
        self.assertEqual(user_stations, {5.0})

        data = received[0]['args'][0]
        self.assertTrue(data['success'])

    def test_user_has_overstationed(self):
        Game.auction_passed_user_ids.write(redis, {
            self.user_2.id
        }, self.game.id)
        Player.stations.write(redis, [6, 7, 8], self.user_3.id)

        with self.user_logged_in(self.user_1.id):
            received = self._create_auction_pass()

        self.notify_mock.assert_called_with(self.game.id)

        step = Game.step.read(redis, self.game.id)
        self.assertEqual(step, StepTypes.STATION_REMOVE)

        turn = Game.turn.read(redis, self.game.id)
        self.assertEqual(turn, self.user_3.id)

        game = Game.get_by_id(redis, self.game.id)

        self.assertEqual(game.auction, {
            'bid': None,
            'station': None,
            'user_id': None,
        })
        self.assertEqual(game.turn, self.user_3.id)
        self.assertEqual(game.auction_passed_user_ids, set())
        self.assertEqual(game.step, StepTypes.STATION_REMOVE)
        self.assertEqual(game.stations, [s for s in self.stations if s != 5.0])

        data = received[0]['args'][0]
        self.assertTrue(data['success'])

    def test_last_user_passed_end_of_auction(self):
        Game.auction.delete(redis, self.game.id)
        Game.auction_user_ids.write(redis, {
            self.user_2.id, self.user_3.id
        }, self.game.id)
        Player.stations.write(redis, [9], self.user_1.id)

        with self.user_logged_in(self.user_1.id):
            received = self._create_auction_pass()

        self.notify_mock.assert_called_with(self.game.id)

        game = Game.get_by_id(redis, self.game.id)

        self.assertEqual(game.auction, {
            'bid': None,
            'station': None,
            'user_id': None,
        })
        self.assertEqual(game.turn, self.user_3.id)
        self.assertEqual(game.auction_passed_user_ids, set())
        self.assertEqual(game.step, StepTypes.RESOURCES_BUY)
        self.assertEqual(game.stations, self.stations)

        data = received[0]['args'][0]
        self.assertTrue(data['success'])
