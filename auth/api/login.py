from flask import request, jsonify
from flask_login import login_user

from auth.models import User


def login():
    if request.method == 'POST':
        data = dict(request.form)

        user = User.get_by_username(data['username'][0])

        login_user(user)
        return jsonify({
            'isAuthenticated': True,
        })
