from auth.models import User
from base.exceptions import EnergynetException

from test.base import BaseTest


class UserModelTestCase(BaseTest):
    def setUp(self):
        super(UserModelTestCase, self).setUp()

        self.user_name = 'test'
        self.user = self.create_user(self.user_name)

    def tearDown(self):
        with self.db.cursor() as cursor:
            cursor = self.db.cursor()
            cursor.execute('delete from public.user *;')
            self.db.commit()

        super(UserModelTestCase, self).tearDown()

    def test_get_by_id(self):
        user = User.get_by_id(
            self.user.id, [User.Fields.ID, User.Fields.NAME], db=self.db
        )
        self.assertEqual(user.id, self.user.id)
        self.assertEqual(user.name, self.user_name)

    def test_create(self):
        self.assertUserExists(self.user_name)

    def test_user_duplicate(self):
        with self.assertRaises(EnergynetException):
            User.create(self.user_name, 'password', db=self.db)
