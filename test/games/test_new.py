from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser

from utils.server import app
from utils.socket_server import io
from utils.redis import redis

from core.models import Game, User, Lobby


class CreateNewTestCase(BaseTest):
    def setUp(self):
        self.user = self.create_user(name='user')

        super(CreateNewTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        User.delete(redis, self.user.id)

        redis.delete(Lobby.key)
        redis.delete(Game.key)

        redis.delete(Game.index())
        redis.delete(User.index())

        super(CreateNewTestCase, self).tearDown()

    @patch('games.api.new.join_room')
    @patch('flask_login.utils._get_user')
    def test_new(self, load_user_mock, join_room_mock):
        load_user_mock.return_value = self.user
        self.client = io.test_client(app, namespace='/games')
        self.client.get_received('/games')

        self.client.emit('new', {
            'name': 'new_game',
            'playersLimit': 4,
        }, namespace='/games')

        received = self.client.get_received('/games')
        self.client.disconnect()

        self.assertEqual(len(received), 2)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        self.assertListEqual(received[1]['args'], [[{
            'name': 'new_game', 'id': 1, 'playersLimit': 4
        }]])

        index = int(redis.get(Game.index()))
        self.assertEqual(Game.owner_id.read(redis, index), self.user.id)
        self.assertEqual(Game.data.read(redis, index), {
            'name': 'new_game',
            'players_limit': 4,
        })
        self.assertEqual(Game.user_ids.read(redis, index), {self.user.id})

        join_room_mock.assert_called_once_with(index)

        redis.delete(Game.owner_id.key(index))
        redis.delete(Game.data.key(index))
        redis.delete(Game.user_ids.key(index))
