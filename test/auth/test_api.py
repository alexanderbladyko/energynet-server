from test.base import BaseTest


class RegisterApiTestCase(BaseTest):
    URL = '/auth/register'

    def setUp(self):
        super(RegisterApiTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor = self.db.cursor()
            cursor.execute('delete from public.user *;')
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
        self.assertEqual(response.status_code, 400)


class LoginApiTestCase(BaseTest):
    URL = '/auth/login'

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        self.user = self.create_user(self.username, self.password)

        super(LoginApiTestCase, self).setUp()

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor = self.db.cursor()
            cursor.execute('delete from public.user *;')
            self.db.commit()

        super(LoginApiTestCase, self).tearDown()

    def test_success(self):
        response = self.client_post(self.URL, data=dict(
            username=self.username,
            password=self.password
        ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, dict(isAuthenticated=True))

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
