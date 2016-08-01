from psycopg2.extras import DictCursor
from flask_testing import TestCase

import app

from auth.models import User
from db.utils import connect_to_db
from helpers.server import app as server


class BaseTest(TestCase):
    def create_app(self):
        server.config['TESTING'] = True
        return server

    @classmethod
    def setUpClass(cls):
        super(BaseTest, cls).setUpClass()
        cls.db = connect_to_db()

    @classmethod
    def tearDownClass(cls):
        super(BaseTest, cls).tearDownClass()
        cls.db.close()

    def create_user(self, user_name='test_user'):
        with self.db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                insert into public.user(name, password)
                values(%s, 'test_password')
                returning id, name, password, salt, created, updated;
            """, (user_name, ))
            user_data = cursor.fetchone()
            self.db.commit()
        if user_data:
            return User(user_data)

    def assertUserExists(self, user_name):
        with self.db.cursor() as cursor:
            cursor.execute(
                'select count(*) from public.user where name=%s;',
                (user_name, )
            )
            user_count, = cursor.fetchone()
        self.assertEqual(user_count, 1)

    def client_get(self, url, user=None):
        with self.app.test_client() as client:
            self._authenticate_client(client, user)

            return client.get(url)

    def client_post(self, url, data, user=None):
        with self.app.test_client() as client:
            self._authenticate_client(client, user)

            return client.post(url, data=data)

    def _authenticate_client(self, client, user):
        if user:
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
                sess['_fresh'] = True
