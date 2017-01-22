from psycopg2 import IntegrityError
from psycopg2.extras import DictCursor
from flask_login import UserMixin

from auth.logic import generate_salt, get_password
from base.exceptions import EnergynetException
from db.utils import get_db
from db.helpers import select, insert


class User(UserMixin):
    DB_TABLE = 'accounts'

    SEQUENCE_NAME = 'accounts_id_seq'

    class Fields:
        ID = 'id'
        NAME = 'name'
        PASSWORD = 'password'
        SALT = 'salt'
        UPDATED = 'updated'
        CREATED = 'created'

    def __init__(self, data):
        self.id = data.get(User.Fields.ID)
        self.name = data.get(User.Fields.NAME)
        self.password = data.get(User.Fields.PASSWORD)
        self.salt = data.get(User.Fields.SALT)
        self.updated = data.get(User.Fields.UPDATED)
        self.created = data.get(User.Fields.CREATED)

    @classmethod
    def get_by_name(cls, name, fields='*', db=None):
        db = get_db()
        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                select(fields, User.DB_TABLE) +
                'WHERE ' + User.Fields.NAME + '=%s;',
                (name,)
            )
            user_data = cursor.fetchone()
        if user_data:
            return User(user_data)
        return None

    @classmethod
    def get_by_id(cls, id, fields='*'):
        db = get_db()
        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                select(fields, User.DB_TABLE) + 'WHERE id=%s;', (id,)
            )
            user_data = cursor.fetchone()
        if user_data:
            return User(user_data)
        return None

    @classmethod
    def create(cls, name, password):
        salt = generate_salt()
        password = get_password(password, salt)

        db = get_db()
        with db.cursor() as cursor:
            try:
                cursor.execute(
                    insert([
                        User.Fields.NAME,
                        User.Fields.PASSWORD,
                        User.Fields.SALT,
                    ], User.DB_TABLE) + 'VALUES (%s, %s, %s)  RETURNING id;',
                    (name, password, salt)
                )
                id = cursor.fetchone()[0]
                db.commit()
            except IntegrityError:
                db.rollback()
                raise EnergynetException('Could not create user')
        return id
