from hashlib import md5
from random import choice
from string import ascii_lowercase, digits


def generate_salt():
    return "".join(choice(ascii_lowercase + digits) for i in range(16))


def get_password(password, salt):
    hashed_password = md5(password.encode("utf-8")).hexdigest()
    combined_hash = hashed_password.encode("utf-8") + salt.encode("utf-8")
    return md5(combined_hash).hexdigest()
