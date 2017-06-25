from flask import request, jsonify

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
            user_token = User.encode_auth_token(user.id)
            return jsonify({
                'id': user.id,
                'isAuthenticated': True,
                'userToken': user_token.decode(),
            })
        else:
            return jsonify({
                'isAuthenticated': False,
            }), 409
