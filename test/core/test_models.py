from core.models import Player, Game
from utils.redis import redis

from test.base import BaseTest


class PlayerCanHoldResourcesTestCase(BaseTest):
    USER_ID = 1

    # Stations used in tests from config
    # stations = {'resources': ['coal', 'oil'], 'cost': 5, 'capacity': 2,
    #     'efficiency': 1},
    # {'resources': ['oil'], 'cost': 7, 'capacity': 3, 'efficiency': 2},
    # {'resources': ['coal'], 'cost': 8, 'capacity': 3, 'efficiency': 2},
    # {'resources': ['oil'], 'cost': 9, 'capacity': 1, 'efficiency': 1},
    # {'resources': ['coal'], 'cost': 10, 'capacity': 2, 'efficiency': 2},
    # {'resources': ['uranium'], 'cost': 11, 'capacity': 1, 'efficiency': 2},

    def setUp(self):
        Player.stations.write(redis, {8, 9, 11}, self.USER_ID)
        Player.resources.write(redis, {
            'coal': 2,
            'oil': 1,
            'uranium': 0,
            'waste': 0,
        }, self.USER_ID)

        super().setUp()

    def tearDown(self):
        Player.delete(redis, self.USER_ID)

        super().tearDown()

    def test_easy_hold(self):
        player = Player.get_by_id(redis, self.USER_ID)
        self.assertEqual(player.can_hold_new_resources(self.test_map_config, {
            'coal': 4,
            'oil': 1,
            'uranium': 2,
            'waste': 0
        }), (True, ''))

    def test_one_resource_left(self):
        player = Player.get_by_id(redis, self.USER_ID)
        self.assertEqual(player.can_hold_new_resources(self.test_map_config, {
            'coal': 4,
            'oil': 2,
            'uranium': 2,
            'waste': 0
        }), (False, 'Not enough space for oil'))

    def test_wrong_kind_of_resource(self):
        player = Player.get_by_id(redis, self.USER_ID)
        self.assertEqual(player.can_hold_new_resources(self.test_map_config, {
            'coal': 4,
            'oil': 1,
            'uranium': 2,
            'waste': 1
        }), (False, 'Not enough space for waste'))

    def test_variation(self):
        Player.stations.delete(redis, self.USER_ID)
        Player.stations.write(redis, {5, 9, 11}, self.USER_ID)

        player = Player.get_by_id(redis, self.USER_ID)

        self.assertEqual(player.can_hold_new_resources(self.test_map_config, {
            'coal': 2,
            'oil': 2,
            'uranium': 2,
            'waste': 0
        }), (False, 'Not enough space for oil'))

    def test_user_has_no_resources(self):
        Player.resources.delete(redis, self.USER_ID)
        player = Player.get_by_id(redis, self.USER_ID)
        self.assertEqual(player.can_hold_new_resources(self.test_map_config, {
            'coal': 4,
            'oil': 1,
            'uranium': 2,
            'waste': 0
        }), (True, ''))


class GetResourcePriceTestCase(BaseTest):
    GAME_ID = 1

    def setUp(self):
        Game.resources.write(redis, {
            'coal': 24,
            'oil': 24,
            'uranium': 12,
            'waste': 24,
        }, self.GAME_ID)

        super().setUp()

    def tearDown(self):
        Game.delete(redis, self.GAME_ID)

        super().tearDown()

    def test_not_enough_game_resources(self):
        Game.resources.write(redis, {
            'coal': 2,
            'oil': 2,
            'uranium': 2,
            'waste': 2,
        }, self.GAME_ID)

        game = Game.get_by_id(redis, self.GAME_ID)

        self.assertEqual(game.get_resource_price(self.test_map_config, {
            'coal': 2,
            'oil': 2,
            'uranium': 3,
            'waste': 2
        }), (False, 0))

    def test_simple(self):
        game = Game.get_by_id(redis, self.GAME_ID)

        self.assertEqual(game.get_resource_price(self.test_map_config, {
            'coal': 2,
            'oil': 2,
            'uranium': 2,
            'waste': 0
        }), (True, 2*1 + 2*1 + 1*1 + 1*2))

    def test_few_groups(self):
        game = Game.get_by_id(redis, self.GAME_ID)

        self.assertEqual(game.get_resource_price(self.test_map_config, {
            'coal': 4,
            'oil': 7,
            'uranium': 2,
            'waste': 0
        }), (True, 3*1 + 1*2 + 3*1 + 3*2 + 1*3 + 1*1 + 1*2))

    def test_from_the_middle(self):
        Game.resources.write(redis, {
            'coal': 19,
            'oil': 20,
            'uranium': 9,
            'waste': 0,
        }, self.GAME_ID)

        game = Game.get_by_id(redis, self.GAME_ID)

        self.assertEqual(game.get_resource_price(self.test_map_config, {
            'coal': 3,
            'oil': 5,
            'uranium': 1,
            'waste': 0
        }), (True, 1*2 + 2*3 + 2*2 + 3*3 + 1*4))
