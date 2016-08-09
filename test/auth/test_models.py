from auth.models import User
from base.exceptions import EnergynetException

from test.base import BaseTest


class UserModelTestCase(BaseTest):
    def setUp(self):
        super(UserModelTestCase, self).setUp()

        self.user_name = 'test'
        self.user_id = User.create(self.user_name, 'password')

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor = self.db.cursor()
            cursor.execute('delete from public.user *;')
            self.db.commit()

        super(UserModelTestCase, self).tearDown()

    def test_get_by_id(self):
        user = User.get_by_id(self.user_id, [User.Fields.ID, User.Fields.NAME])
        self.assertEqual(user.id, self.user_id)
        self.assertEqual(user.name, self.user_name)

    def test_create(self):
        self.assertUserExists(self.user_name)

    def test_user_duplicate(self):
        with self.assertRaises(EnergynetException):
            User.create(self.user_name, 'password')
