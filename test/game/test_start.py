from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser
from core.constants import StepTypes
from core.models import Game, User, Lobby, Player

from utils.redis import redis

from test import factories


class StartGameTestCase(BaseTest):
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
        self.lobby = factories.LobbyFactory.create(self.game.id)

        Game.user_ids.write(redis, self.user_ids, self.game.id)

        super(StartGameTestCase, self).setUp()

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
        redis.delete(Lobby.key)
        redis.delete(Game.key)

        redis.delete(Game.index())
        redis.delete(User.index())

        super(StartGameTestCase, self).tearDown()

    def test_start(self):
        stations = [1.0, 2.0, 3.0, 4.0]
        with patch(
            'game.api.game.start.get_start_stations', return_value=stations
        ):
            with patch('game.logic.emit') as emit_mock:
                with self.user_logged_in(self.db_user_1.id):
                    with patch('config.config', self.map_config_mock):
                        client = self.create_test_client()

                        client.emit('game', {})
                        client.get_received()

                        client.emit('game_start', {})

                        received = client.get_received()

                        client.disconnect()

        self.assertEqual(emit_mock.call_count, 1)
        name, data = emit_mock.call_args[0]
        room = emit_mock.call_args[1]['room']
        self.assertEqual(name, 'game')
        ordered_user_ids = Game.order.read(redis, self.game.id)
        first_user_id = ordered_user_ids[0]
        self.assertEqual(list(set(self.user_ids)), list(set(ordered_user_ids)))
        self.assertEqual(data['meta'], {
            'phase': None,
            'data': {
                'playersLimit': 3,
                'name': 'game1'
            },
            'id': self.game.id,
            'map': self.map,
            'turn': first_user_id,
            'stations': stations,
            'ownerId': self.user_1.id,
            'step': StepTypes.COLORS,
            'auction': {
                'bid': None,
                'station': None,
                'userId': None,
            },
            'areas': [],
            'userIds': self.user_ids,
            'resources': {
                'uranium': 7, 'coal': 18, 'oil': 24, 'waste': 0
            },
            'order': ordered_user_ids,
        })
        self.assertEqual(data['data'], [
            {
                'color': None,
                'cities': {},
                'cash': 33,
                'data': {
                    'name': 'user_1',
                    'avatar': None,
                },
                'resources': {
                    'waste': None,
                    'oil': None,
                    'coal': None,
                    'uranium': None
                },
                'id': self.user_1.id,
                'stations': []
            },
            {
                'color': None,
                'cities': {},
                'cash': 33,
                'data': {
                    'name': 'user_2',
                    'avatar': None,
                },
                'resources': {
                    'waste': None,
                    'oil': None,
                    'coal': None,
                    'uranium': None
                },
                'id': self.user_2.id,
                'stations': []
            }, {
                'color': None,
                'cities': {},
                'cash': 33,
                'data': {
                    'name': 'user_3',
                    'avatar': None,
                },
                'resources': {
                    'waste': None,
                    'oil': None,
                    'coal': None,
                    'uranium': None
                },
                'id': self.user_3.id,
                'stations': []
            }
        ])

        self.assertEqual(room, 'games:%s' % self.game.id)

        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertIsNone(User.current_lobby_id.read(redis, self.user_1.id))
        self.assertEqual(
            Game.user_ids.read(redis, self.game.id), set(self.user_ids)
        )
        self.assertEqual(Game.step.read(redis, self.game.id), StepTypes.COLORS)
        self.assertFalse(redis.sismember(Lobby.key, self.game.id))
        for user_id in self.user_ids:
            self.assertIsNone(User.current_lobby_id.read(redis, user_id))
            self.assertEqual(
                Player.cash.read(redis, user_id),
                self.test_map_config['startCash']
            )

    def test_not_enough_players(self):
        redis.srem(Game.user_ids.key(self.game.id), self.user_3.id)
        with patch('config.config', self.map_config_mock):
            with self.user_logged_in(self.db_user_1.id):
                client = self.create_test_client()
                client.get_received()

                client.emit('game_start', {})

                received = client.get_received()

                client.disconnect()

        self.assertEqual(len(received), 1)
        self.assertFalse(received[0]['args'][0]['success'])

    def test_user_is_not_in_the_game(self):
        redis.delete(User.current_game_id.key(self.user_1.id))
        redis.delete(User.current_lobby_id.key(self.user_1.id))
        with patch('config.config', self.map_config_mock):
            with self.user_logged_in(self.db_user_1.id):
                client = self.create_test_client()
                client.get_received()

                client.emit('game_start', {})

                received = client.get_received()

                client.disconnect()

        self.assertEqual(len(received), 1)
        self.assertFalse(received[0]['args'][0]['success'])

    def test_user_is_not_the_owner(self):
        with patch('config.config', self.map_config_mock):
            with self.user_logged_in(self.db_user_2.id):
                client = self.create_test_client()
                client.get_received()

                client.emit('game_start', {})

                received = client.get_received()

                client.disconnect()

        self.assertEqual(len(received), 1)
        self.assertFalse(received[0]['args'][0]['success'])
