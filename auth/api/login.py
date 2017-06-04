from flask import request, jsonify
from flask_login import login_user

from auth.logic import get_password
from auth.models import User


def login():
    if request.method == 'POST':
        data = request.get_json()

        user = User.get_by_name(data['username'], [
            User.Fields.ID,
            User.Fields.PASSWORD,
            User.Fields.SALT,
        ])
        password = data['password']
        result_password = get_password(password, user.salt)

        if result_password == user.password:
            if login_user(user, remember=True):
                return jsonify({
                    'isAuthenticated': True,
                })
            else:
                return jsonify({
                    'isAuthenticated': False,
                }), 409
        else:
            return jsonify({
                'isAuthenticated': False,
            }), 409
