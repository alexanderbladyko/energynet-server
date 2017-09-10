from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser
from core.constants import StepTypes
from core.models import Game, User, Player

from utils.redis import redis

from test import factories


class CitiesBuyTestCase(BaseTest):
    def setUp(self):
        self.db_user_1 = self.create_user(name='user_1')
        self.db_user_2 = self.create_user(name='user_2')
        self.db_user_3 = self.create_user(name='user_3')

        self.areas = {'area1', 'area2', 'area4', 'area5', 'area6'}
        self.game = factories.GameFactory.create(
            data={'name': 'game1', 'players_limit': 3},
            turn=self.db_user_1.id,
            owner_id=self.db_user_1.id,
            map=self.map,
            user_ids={self.db_user_1.id, self.db_user_2.id, self.db_user_3.id},
            order=[self.db_user_2.id, self.db_user_3.id, self.db_user_1.id],
            step=StepTypes.CITIES_BUY,
            areas=self.areas,
            phase=1,
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
        for user_id in self.user_ids:
            Player.cash.write(redis, 50, user_id)

        Player.cities.write(redis, {
            'samara': 10,
            'cheboksary': 10,
        }, self.user_1.id)
        Player.cities.write(redis, {
            'nizhnekamsk': 10,
            'ulyanovsk': 10,
        }, self.user_2.id)
        Player.cities.write(redis, {
            'ufa': 10,
            'ulyanovsk': 15,
            'kazan': 10,
        }, self.user_3.id)

        self.notify_patcher = patch('game.api.resources.notify_game_players')
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

    def _send_cities_buy(self, cities):
        client = self.create_test_client()
        client.get_received()

        client.emit('cities_buy', {'cities': cities})
        received = client.get_received()
        client.disconnect()

        return received

    def test_not_your_turn(self):
        with self.user_logged_in(self.user_2.id):
            received = self._send_cities_buy(['orenburg'])

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_incorrect_step(self):
        Game.step.write(redis, StepTypes.AUCTION, self.game.id)
        with self.user_logged_in(self.user_1.id):
            received = self._send_cities_buy(['orenburg', 'nizhnekamsk'])

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_city_already_owned(self):
        with self.user_logged_in(self.user_1.id):
            received = self._send_cities_buy(['orenburg', 'cheboksary'])

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_outside_of_area(self):
        with self.user_logged_in(self.user_1.id):
            received = self._send_cities_buy(['saratov', 'nizhnekamsk'])

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_no_slots_for_ulyanovsk(self):
        redis.hmset(Player.cities.key(self.user_2.id), {'ulyanovsk': 10})
        redis.hmset(Player.cities.key(self.user_3.id), {'ulyanovsk': 15})
        with self.user_logged_in(self.user_1.id):
            received = self._send_cities_buy(['ulyanovsk', 'nizhnekamsk'])

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_not_enough_cash(self):
        with self.user_logged_in(self.user_1.id):
            received = self._send_cities_buy([
                'orenburg', 'nizhnekamsk', 'ufa', 'chelyabinsk'
            ])

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_correct_city_buy(self):
        with self.user_logged_in(self.user_1.id):
            received = self._send_cities_buy(['orenburg', 'nizhnekamsk'])

        data = received[0]['args'][0]
        self.assertTrue(data['success'])
        game = Game.get_by_id(redis, self.game.id)
        self.assertEqual(game.turn, self.user_3.id)
        self.assertEqual(game.step, StepTypes.CITIES_BUY)

        player = Player.get_by_id(redis, self.user_1.id)
        self.assertEqual(player.cash, 14)

    def test_correct_city_buy_next_step(self):
        Game.order.delete(redis, self.game.id)
        Game.order.write(redis, [
            self.user_1.id, self.user_3.id, self.user_2.id
        ], self.game.id)
        with self.user_logged_in(self.user_1.id):
            received = self._send_cities_buy(['orenburg', 'nizhnekamsk'])

        data = received[0]['args'][0]
        self.assertTrue(data['success'])
        game = Game.get_by_id(redis, self.game.id)
        self.assertEqual(game.turn, self.user_2.id)
        self.assertEqual(game.step, StepTypes.FINANCE_RECEIVE)

        player = Player.get_by_id(redis, self.user_1.id)
        self.assertEqual(player.cash, 14)
