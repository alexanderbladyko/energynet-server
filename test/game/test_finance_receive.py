from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser
from core.constants import StepTypes
from core.models import Game, User, Player

from utils.redis import redis

from test import factories


class FinanceReceiveTestCase(BaseTest):
    def setUp(self):
        self.db_user_1 = self.create_user(name='user_1')
        self.db_user_2 = self.create_user(name='user_2')
        self.db_user_3 = self.create_user(name='user_3')

        self.initial_resources = {
            'coal': 20,
            'oil': 17,
            'uranium': 10,
            'waste': 22,
        }

        self.game = factories.GameFactory.create(
            data={'name': 'game1', 'players_limit': 3},
            turn=self.db_user_1.id,
            owner_id=self.db_user_1.id,
            map=self.map,
            user_ids={self.db_user_1.id, self.db_user_2.id, self.db_user_3.id},
            order=[self.db_user_1.id, self.db_user_2.id, self.db_user_3.id],
            step=StepTypes.FINANCE_RECEIVE,
            resources=self.initial_resources,
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

        # Stations used in tests from config
        # stations = {'resources': ['coal', 'oil'], 'cost': 5, 'capacity': 2,
        #     'efficiency': 1},
        # {'resources': ['oil'], 'cost': 7, 'capacity': 3, 'efficiency': 2},
        Player.resources.write(redis, {
            'coal': 2,
            'oil': 1,
            'uranium': 0,
            'waste': 0,
        }, self.user_1.id)
        Player.cash.write(redis, 10, self.user_1.id)
        Player.stations.write(redis, {5.0, 7.0}, self.user_1.id)
        Player.cities.write(redis, {
            'samara': 10,
            'cheboksary': 10,
            'chelyabinsk': 10,
        }, self.user_1.id)

        self.notify_patcher = patch(
            'game.api.finance.notify_game_players'
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

    def _send_finance_receive(self, data):
        client = self.create_test_client()
        client.get_received()

        client.emit('finance_receive', data)
        received = client.get_received()
        client.disconnect()

        return received

    def test_finance_receive(self):
        with self.user_logged_in(self.db_user_1.id):
            received = self._send_finance_receive({
                'stations': {
                    5.0: {
                        'coal': 1,
                        'oil': 1,
                        'waste': 0,
                        'uranium': 0,
                    }
                }
            })

        self.notify_mock.assert_called_with(self.game.id)

        # game = Game.get_by_id(redis, self.game.id)

        player = Player.get_by_id(redis, self.user_1.id)
        self.assertEqual(player.resources, {
            'coal': 1,
            'oil': 0,
            'uranium': 0,
            'waste': 0,
        })
        self.assertEqual(player.stations, {5.0, 7.0})
        self.assertEqual(player.cash, 10 + self.test_map_config['payment'][1])

        data = received[0]['args'][0]
        self.assertEqual(data, {'success': True})

    def test_stations_are_not_matching(self):
        with self.user_logged_in(self.db_user_1.id):
            received = self._send_finance_receive({
                'stations': {
                    6.0: {
                        'coal': 1,
                        'oil': 1,
                        'waste': 0,
                        'uranium': 0,
                    }
                }
            })

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_wrong_resources(self):
        with self.user_logged_in(self.db_user_1.id):
            received = self._send_finance_receive({
                'stations': {
                    5.0: {
                        'coal': 1,
                        'oil': 1,
                        'waste': 1,
                        'uranium': 0,
                    }
                }
            })

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_not_enough_resources_for_station(self):
        with self.user_logged_in(self.db_user_1.id):
            received = self._send_finance_receive({
                'stations': {
                    5.0: {
                        'coal': 0,
                        'oil': 1,
                        'waste': 0,
                        'uranium': 0,
                    }
                }
            })

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_not_enough_resources(self):
        with self.user_logged_in(self.db_user_1.id):
            received = self._send_finance_receive({
                'stations': {
                    7.0: {
                        'coal': 0,
                        'oil': 3,
                        'waste': 0,
                        'uranium': 0,
                    }
                }
            })

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_not_your_turn(self):
        Game.turn.write(redis, self.user_2.id, self.game.id)
        with self.user_logged_in(self.user_1.id):
            received = self._send_finance_receive({
                'stations': {
                    5.0: {
                        'coal': 1,
                        'oil': 1,
                        'waste': 0,
                        'uranium': 0,
                    }
                }
            })

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_incorrect_step(self):
        Game.step.write(redis, StepTypes.AUCTION, self.game.id)
        with self.user_logged_in(self.user_1.id):
            received = self._send_finance_receive({
                'stations': {
                    5.0: {
                        'coal': 1,
                        'oil': 1,
                        'waste': 0,
                        'uranium': 0,
                    }
                }
            })

        data = received[0]['args'][0]
        self.assertFalse(data['success'])
