from psycopg2.extras import DictCursor
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from flask_testing import TestCase

import app

from auth.logic import get_password
from auth.models import User
from db.utils import connect_to_db
from utils.server import app as server
from utils.redis import redis


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

    def tearDown(self):
        super(BaseTest, self).tearDown()

        self._check_isolation()

    def _check_isolation(self):
        tables = [
            User
        ]
        with self.db.cursor() as cursor:
            for table in tables:
                cursor.execute('select * from public.%s;' % table.DB_TABLE)
                break
        self.assertEqual(
            cursor.rowcount, 0, 'Isolation leaked for: %s' % table.DB_TABLE
        )

        self.assertFalse(redis.keys())

    def create_user(self, name='test_user', password='test_password'):
        salt = 'test_salt'
        generated_password = get_password(password, salt)
        with self.db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                insert into public.user(name, password, salt)
                values(%s, %s, %s)
                returning id, name, password, salt, created, updated;
            """, (name, generated_password, salt))
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
            self.authenticate_client(client, user)

            return client.get(url)

    def client_post(self, url, data, user=None):
        with self.app.test_client() as client:
            self.authenticate_client(client, user)

            return client.post(url, data=data)

    def authenticate_client(self, client, user):
        if user:
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
                sess['_fresh'] = True

    def assertResponseSchema(self, response, schema):
        try:
            validate(response, schema)
        except ValidationError as error:
            self.fail(error.message)
