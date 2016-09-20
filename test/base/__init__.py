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

        cls._reset_indexes()

    @classmethod
    def tearDownClass(cls):
        super(BaseTest, cls).tearDownClass()
        cls.db.close()

    def tearDown(self):
        super(BaseTest, self).tearDown()

        self._check_isolation()

    @classmethod
    def _reset_indexes(cls):
        sequences = [
            User.SEQUENCE_NAME,
        ]
        with cls.db.cursor() as cursor:
            for sequence in sequences:
                cursor.execute('ALTER SEQUENCE %s RESTART WITH 1;' % sequence)
            cls.db.commit()

    def _check_isolation(self):
        tables = [
            User
        ]
        with self.db.cursor() as cursor:
            for table in tables:
                cursor.execute(
                    "select count(*) from {0};".format(table.DB_TABLE)
                )
                count = cursor.fetchone()[0]
                if count != 0:
                    self.fail('Isolation leaked for: %s' % table.DB_TABLE)
                    break

        self.assertFalse(redis.keys())

    def create_user(self, name='test_user', password='test_password'):
        salt = 'test_salt'
        generated_password = get_password(password, salt)
        with self.db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                insert into public.{0}(name, password, salt)
                values('{1}', '{2}', '{3}')
                returning id, name, password, salt, created, updated;
            """.format(User.DB_TABLE, name, generated_password, salt))
            user_data = cursor.fetchone()
            self.db.commit()
        if user_data:
            return User(user_data)

    def assertUserExists(self, user_name):
        with self.db.cursor() as cursor:
            cursor.execute(
                "select count(*) from public.{0} where name='{1}';".format(
                    User.DB_TABLE, user_name
                )
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

    def assertRedisList(self, values, key):
        self._assertList(
            values, [v.decode('utf-8') for v in redis.lrange(key, 0, -1)]
        )

    def assertRedisListInt(self, values, key):
        self._assertList(
            values, [int(v.decode('utf-8')) for v in redis.lrange(key, 0, -1)]
        )

    def _assertList(self, list_1, list_2):
        self.assertEqual(len(list_1), len(list_2))
        self.assertListEqual(sorted(list_1), sorted(list_2))

    def assertRedisInt(self, value, key):
        self.assertEqual(value, int(redis.get(key).decode('utf-8')))

    def assertRedisValue(self, value, key):
        self.assertEqual(value, redis.get(key).decode('utf-8'))
