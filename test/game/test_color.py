from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser
from core.constants import StepTypes
from core.models import Game, User, Player

from utils.redis import redis

from test import factories


class TestColorChooseTestCase(BaseTest):
    def setUp(self):
        self.db_user_1 = self.create_user(name='user_1')
        self.db_user_2 = self.create_user(name='user_2')
        self.db_user_3 = self.create_user(name='user_3')

        # Colors from fake config
        # '#bc3029',
        # '#d8dd37',
        # '#48d635',
        # '#2c97c1',
        # '#393a3a',
        # '#c66ad8'

        self.game = factories.GameFactory.create(
            data={'name': 'game1', 'players_limit': 3},
            owner_id=self.db_user_1.id,
            map=self.map,
            user_ids={self.db_user_1.id, self.db_user_2.id, self.db_user_3.id},
            step=StepTypes.COLORS,
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

        self.notify_patcher = patch('game.api.color.notify_game_players')
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

    def _create_color_choose(self, data):
        client = self.create_test_client()
        client.get_received()

        client.emit('color_choose', data)
        received = client.get_received()
        client.disconnect()

        return received

    def test_color_choose(self):
        with self.user_logged_in(self.db_user_1.id):
            received = self._create_color_choose({
                'color': '#bc3029',
            })

        self.notify_mock.assert_called_with(self.game.id)

        game = Game.get_by_id(redis, self.game.id)
        self.assertEqual(game.reserved_colors, {'#bc3029'})

        player = Player.get_by_id(redis, self.user_1.id)
        self.assertEqual(player.color, '#bc3029')

        data = received[0]['args'][0]
        self.assertEqual(data, {'success': True})

    def test_color_choose_game_start(self):
        Game.reserved_colors.write(redis, {
            '#393a3a',
            '#2c97c1',
        }, self.game.id)
        with self.user_logged_in(self.db_user_1.id):
            received = self._create_color_choose({
                'color': '#bc3029',
            })

        self.notify_mock.assert_called_with(self.game.id)

        game = Game.get_by_id(redis, self.game.id)
        self.assertEqual(game.reserved_colors, {
            '#bc3029', '#393a3a', '#2c97c1',
        })
        self.assertEqual(game.step, StepTypes.AUCTION)

        player = Player.get_by_id(redis, self.user_1.id)
        self.assertEqual(player.color, '#bc3029')

        data = received[0]['args'][0]
        self.assertEqual(data, {'success': True})

    def test_player_has_color(self):
        Player.color.write(redis, '#bc3029', self.user_1.id)
        with self.user_logged_in(self.db_user_1.id):
            received = self._create_color_choose({
                'color': '#bc3029',
            })

        self.notify_mock.assert_not_called()

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_color_is_taken(self):
        Game.reserved_colors.write(redis, {
            '#bc3029',
            '#2c97c1',
        }, self.game.id)
        with self.user_logged_in(self.db_user_1.id):
            received = self._create_color_choose({
                'color': '#bc3029',
            })

        self.notify_mock.assert_not_called()

        data = received[0]['args'][0]
        self.assertFalse(data['success'])

    def test_invalid_color(self):
        with self.user_logged_in(self.db_user_1.id):
            received = self._create_color_choose({
                'color': '#222222',
            })

        self.notify_mock.assert_not_called()

        data = received[0]['args'][0]
        self.assertFalse(data['success'])
