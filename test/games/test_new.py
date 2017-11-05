from unittest.mock import patch
from test.base import BaseTest

from auth.models import User as DbUser

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

    def test_new(self):
        with patch('games.api.new.join_game') as join_game_mock:
            with patch('games.api.new.unsubscribe_from_games') as unsub_mock:
                with self.user_logged_in(self.user.id):
                    client = self.create_test_client()
                    client.get_received()

                    client.emit('games_new', {
                        'name': 'new_game',
                        'playersLimit': 4,
                        'map': self.map,
                        'areas': ['area1', 'area2', 'area3'],
                    })

                    received = client.get_received()
                    client.disconnect()

        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], [{'success': True}])
        # self.assertListEqual(received[1]['args'], [[{
        #     'name': 'new_game', 'id': 1, 'playersLimit': 4
        # }]])

        index = int(redis.get(Game.index()))
        game = Game.get_by_id(redis, index)
        self.assertEqual(game.owner_id, self.user.id)
        self.assertEqual(game.data, {
            'name': 'new_game',
            'players_limit': 4,
        })
        self.assertEqual(game.areas, {'area1', 'area2', 'area3'})
        self.assertEqual(game.user_ids, {self.user.id})

        join_game_mock.assert_called_once_with(index)
        unsub_mock.assert_called_once_with()

        redis.delete(Game.areas.key(index))
        redis.delete(Game.map.key(index))
        redis.delete(Game.owner_id.key(index))
        redis.delete(Game.data.key(index))
        redis.delete(Game.user_ids.key(index))
        redis.delete(Game.phase.key(index))
