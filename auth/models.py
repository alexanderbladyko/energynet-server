from flask_login import UserMixin

from auth.logic import generate_salt, get_password
from db.utils import get_db


class User(UserMixin):
    users = [
        ('admin', 'admin'),
    ]

    def __init__(
        self, id, username, salt=None, password=None, created=None,
        updated=None
    ):
        self.id = id
        self.username = username
        self.password = password
        self.salt = salt
        self.updated = updated
        self.created = created

    @classmethod
    def get_by_username(cls, username):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, name, salt, password, created, updated
            FROM public."user"
            WHERE name=%s;
        """, (username,))
        user_data = cursor.fetchone()
        cursor.close()
        if user_data:
            return User(*user_data)
        return None

    @classmethod
    def get_by_id(cls, id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, name, salt, password, created, updated
            FROM public."user"
            WHERE id=%s;
        """, (id,))
        user_data = cursor.fetchone()
        cursor.close()
        if user_data:
            return User(*user_data)
        return None

    @classmethod
    def create(cls, name, password):
        salt = generate_salt()
        password = get_password(password, salt)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO public."user"(
                name, password, salt, created, updated
            )
            VALUES (%s, %s, %s, now(), now());
        """, (name, password, salt))
        db.commit()

        cursor.close()
