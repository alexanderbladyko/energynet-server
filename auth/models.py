from flask_login import UserMixin


class User(UserMixin):
    users = [
        ('admin', 'admin'),
    ]

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_id(self):
        return '1'

    @classmethod
    def get_by_username(cls, requested_username):
        for username, password in cls.users:
            if username == requested_username:
                return User(username, password)
        return None

    @classmethod
    def get_by_id(cls, id):
        user = cls.users[0]
        if user:
            name, password = user
            return User(name, password)
