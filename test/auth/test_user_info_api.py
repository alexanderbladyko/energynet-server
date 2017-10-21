from test.base import BaseTest

from auth.models import User


class UserInfoApiTestCase(BaseTest):
    LOGIN_URL = '/auth/login'
    URL = '/auth/user_info'

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        self.user = self.create_user(self.username, self.password)

        super(UserInfoApiTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor.execute("delete from {0};".format(User.DB_TABLE))
            self.db.commit()

        super(UserInfoApiTestCase, self).tearDown()

    def test_success(self):
        token = User.encode_auth_token(self.user.id)
        with self.app.test_client() as client:
            response = client.get(
                self.URL,
                content_type='application/json',
                headers={'Authorization': token}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            'id': self.user.id,
            'isAuthenticated': True,
            'userToken': token.decode('utf8'),
        })

    def test_fail_login(self):
        with self.app.test_client() as client:
            response = client.get(
                self.URL,
                content_type='application/json',
                headers={'Authorization': 'token_shmoken'}
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            'isAuthenticated': False,
            'userToken': 'token_shmoken',
        })
