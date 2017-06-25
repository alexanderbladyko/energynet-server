from test.base import BaseTest

from auth.models import User as DbUser

from utils.redis import redis


class SocketApiTestCase(BaseTest):
    def setUp(self):
        self.username = 'test_user'
        self.user = self.create_user(self.username)

        super(SocketApiTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        super(SocketApiTestCase, self).tearDown()

    def test_connect(self):
        with self.user_logged_in(self.user.id):
            client = self.create_test_client()
            received = client.get_received()
            client.disconnect()

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'][0], {
            'id': self.user.id,
        })

        redis.delete('user')
        redis.delete('user:%d:data' % self.user.id)
