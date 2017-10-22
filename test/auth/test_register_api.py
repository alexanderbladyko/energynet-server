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
