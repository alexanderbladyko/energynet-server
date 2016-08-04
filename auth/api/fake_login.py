from flask import jsonify
from flask_login import login_user

from auth.models import User


def fake_login(user_id):
    user = User.get_by_id(user_id)

    if not user:
        return "No such user"

    login_user(user)

    return jsonify({
        'isAuthenticated': True,
    })
