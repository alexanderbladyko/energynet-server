import os

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
                'game.api.game.start.get_start_stations',
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
        directory = 'test/e2e/scenarios/' + scenario_name
        files = []
        for filename in os.listdir(directory + '/rounds'):
            if filename.endswith(".yaml"):
                files.append(int(filename[:-5]))

        files.sort()

        scenario = load(open(os.path.join(directory, 'base.yaml')))
        scenario['steps'] = []
        for file_index in files:
            file_path = os.path.join(
                directory, 'rounds/{}.yaml'.format(file_index)
            )
            step_data = load(open(file_path, 'r'))
            scenario['steps'] = scenario['steps'] + step_data['steps']

        self.scenario = scenario

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
            if received_message['name'] != game_step['action']:
                self.fail('Could not find action for {} step'.format(
                    game_step
                ))
            self.assertTrue(
                received_message['args'][0]['success'], game_step
            )
            assert_section = game_step['assert']
            self.assert_game(assert_section.get('game'), game_step)
            self.assert_users(assert_section.get('users'), game_step)
            self.assert_players(assert_section.get('players'), game_step)

    def assert_users(self, users_data, game_step):
        if not users_data:
            return
        for user_id, assert_data in users_data.items():
            user = User.get_by_id(redis, user_id)
            for key, value in assert_data.items():
                actual, expected = self._transform_to_comparable(
                    value, getattr(user, key)
                )
                self.assertEqual(
                    actual, expected, self._get_error_message(game_step, key, user)
                )

    def assert_game(self, game_data, game_step):
        if not game_data:
            return
        game = Game.get_by_id(redis, self.game_info['id'])
        for key, value in game_data.items():
            actual, expected = self._transform_to_comparable(
                value, getattr(game, key)
            )

            self.assertEqual(
                actual, expected, self._get_error_message(game_step, key, game)
            )

    def assert_players(self, players_data, game_step):
        if not players_data:
            return
        for user_id, assert_data in players_data.items():
            player = Player.get_by_id(redis, user_id)
            for key, value in assert_data.items():
                actual, expected = self._transform_to_comparable(
                    value, getattr(player, key)
                )
                self.assertEqual(
                    actual, expected,
                    self._get_error_message(game_step, key, player)
                )

    def _transform_to_comparable(self, expected, actual):
        actual_result = actual
        expected_result = expected
        if isinstance(actual, set) and isinstance(expected, list):
            expected_result = set(expected)
            if len(expected) != len(expected_result):
                self.fail('Set "{}" is supposed to have unique values'.format(
                    expected,
                ))

        if isinstance(expected, dict):
            if 'from' in expected or 'to' in expected:
                actual_result = actual[
                    expected.get('from'): expected.get('to')
                ]
                expected_result = expected.get('data')
        return actual_result, expected_result

    def _get_error_message(self, game_step, field, obj):
        return 'User {} action {} with data {} has error \
in {} object {} with "{}" field'.format(
            game_step['user'],
            game_step['action'],
            game_step.get('data'),
            obj.__class__.__name__,
            obj.id,
            field,
        )
