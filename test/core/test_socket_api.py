from unittest.mock import patch
from test.base import BaseTest

from utils.server import app
from utils.socket_server import io
from utils.redis import redis


class SocketApiTestCase(BaseTest):
    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        self.user = self.create_user(self.username, self.password)

        super(SocketApiTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute('delete from public.user *;')
            self.db.commit()

        super(SocketApiTestCase, self).tearDown()

    @patch('flask_login._get_user')
    def test_connect(self, load_user_mock):
        load_user_mock.return_value = self.user

        client = io.test_client(app)
        received = client.get_received()

        self.assertEqual(len(received), 1)
        self.assertListEqual(received[0]['args'], ['test'])
        client.disconnect()

        redis.delete('user')
        redis.delete('user:%d:data' % self.user.id)
