from flask import request, jsonify, abort
from flask_login import login_user

from auth.logic import get_password
from auth.models import User


def login():
    if request.method == 'POST':
        data = dict(request.form)

        user = User.get_by_name(data['username'][0], [
            User.Fields.ID,
            User.Fields.PASSWORD,
            User.Fields.SALT,
        ])
        password = data['password'][0]
        result_password = get_password(password, user.salt)

        if result_password == user.password:
            login_user(user)
            return jsonify({
                'isAuthenticated': True,
            })
        else:
            return jsonify({
                'isAuthenticated': False,
            }), 409
