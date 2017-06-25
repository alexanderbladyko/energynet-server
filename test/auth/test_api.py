import json
from unittest import skip, mock

from test.base import BaseTest

from auth.models import User as DbUser


class RegisterApiTestCase(BaseTest):
    URL = '/auth/register'

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        super(RegisterApiTestCase, self).tearDown()

    def test_success(self):
        username = 'test_user'
        password = 'test_password'
        response = self.client_post(self.URL, data=dict(
            username=username,
            password=password
        ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, dict(success=True))
        self.assertUserExists(username)

    def test_user_duplicate(self):
        username = 'test_user'
        self.create_user(username)
        response = self.client_post(self.URL, data=dict(
            username=username,
            password='some_password'
        ))
        self.assertEqual(response.status_code, 409)
        self.assertFalse(response.json['success'])

    def test_authorized_user(self):
        username = 'test_user'
        user = self.create_user(username)
        response = self.client_post(self.URL, data=dict(
            username=username,
            password='some_password'
        ), user=user)
        self.assertEqual(response.status_code, 409)


class LoginApiTestCase(BaseTest):
    URL = '/auth/login'

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        self.user = self.create_user(self.username, self.password)

        super(LoginApiTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        super(LoginApiTestCase, self).tearDown()

    def test_success(self):
        with mock.patch('auth.models.User.encode_auth_token') as encode_mock:
            with self.app.test_client() as client:
                token = mock.MagicMock()
                token.decode = mock.MagicMock(return_value='<token>')
                encode_mock.return_value = token
                response = client.post(self.URL, data=json.dumps(dict(
                    username=self.username,
                    password=self.password
                )), content_type='application/json')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {
                'id': self.user.id,
                'isAuthenticated': True,
                'userToken': '<token>',
            })

    def test_fail_login(self):
        response = self.client_post(self.URL, data=dict(
            username=self.username,
            password='some_password'
        ))
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json, dict(isAuthenticated=False))

    def test_get(self):
        response = self.client_get(self.URL)
        self.assertEqual(response.status_code, 405)


class LogoutApiTestCase(BaseTest):
    URL = '/auth/logout'

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        self.user = self.create_user(self.username, self.password)

        super(LogoutApiTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(DbUser.DB_TABLE))
            self.db.commit()

        super(LogoutApiTestCase, self).tearDown()

    @skip
    def test_success_get(self):
        with self.app.test_client() as client:
            self.authenticate_client(client, self.user)

            response = client.get(self.URL)

            with client.session_transaction() as sess:
                self.assertTrue('user_id' not in sess)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, dict(success=True))

    @skip
    def test_success_post(self):
        with self.app.test_client() as client:
            self.authenticate_client(client, self.user)

            response = client.post(self.URL)

            with client.session_transaction() as sess:
                self.assertTrue('user_id' not in sess)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, dict(success=True))
