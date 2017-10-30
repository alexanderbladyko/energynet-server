from yaml import load
from unittest.mock import patch

from auth.models import User as DbUser
from core.models import Game, User, Player
from utils.redis import redis

from test.base import BaseTest


class FakeRandomShuffle:
    def __init__(self, return_value):
        self.return_value = return_value

    def shuffle(self, list_to_shuffle):
        list_to_shuffle.clear()
        list_to_shuffle.extend(self.return_value)


class BaseScenariosTestCase(BaseTest):
    scenario_name = NotImplemented

    def setUp(self):
        super().setUp()

        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        self._load_scenario(self.scenario_name)
        self._init_users()
        self.steps = self.scenario.get('steps')
        self.game_info = self.scenario.get('game')

        game = self.scenario.get('game')
        self.patchers = [
            patch(
                'game.logic.get_start_stations',
                return_value=game.get('first_station_order')
            ),
            patch(
                'game.api.game.start.random',
                FakeRandomShuffle(game.get('first_order'))
            ),
            patch('config.config', self.map_config_mock),
        ]
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        redis.flushdb()

        for patcher in self.patchers:
            patcher.stop()

        super().tearDown()

    def _load_scenario(self, scenario_name):
        self.scenario = load(
            open('test/e2e/scenarios/' + scenario_name + '/moves.yaml', 'r')
        )

    def _init_users(self):
        for user in self.scenario.get('users'):
            self.create_user_with_id(user.get('id'), user.get('name'))

    def run_steps(self):
        client = self.create_test_client()
        client.get_received()

        for game_step in self.steps:
            self.run_step(client, game_step)

        client.disconnect()

    def run_step(self, client, game_step):
        with self.user_logged_in(game_step['user']):
            client.emit(game_step['action'], game_step.get('data'))
            received = client.get_received()
            for received_message in received:
                if received_message['name'] == game_step['action']:
                    break
            self.assertTrue(
                received_message['args'][0]['success'], game_step
            )
            assert_section = game_step['assert']
            self.assert_game(assert_section.get('game'), game_step)
            self.assert_users(assert_section.get('users'), game_step)

    def assert_users(self, users_data, game_step):
        if not users_data:
            return
        for user_id, assert_data in users_data.items():
            user = User.get_by_id(redis, user_id)
            for key, value in assert_data.items():
                self.assertEqual(
                    getattr(user, key), value, self._get_error_message(
                        game_step, key
                    )
                )

    def assert_game(self, game_data, game_step):
        if not game_data:
            return
        game = Game.get_by_id(redis, self.game_info['id'])
        for key, value in game_data.items():
            actual_data = getattr(game, key)
            expected_data = value
            if isinstance(actual_data, set):
                actual_data = list(actual_data)
            if isinstance(expected_data, dict):
                if 'from' in expected_data or 'to' in expected_data:
                    actual_data = actual_data[
                        expected_data.get('from'): expected_data.get('to')
                    ]
                    expected_data = expected_data.get('data')
            self.assertEqual(
                actual_data, expected_data, self._get_error_message(
                    game_step, key
                )
            )

    def _get_error_message(self, game_step, field):
        return 'Action {} with data {} has error in {} field'.format(
            game_step['action'],
            game_step.get('data'),
            field,
        )
