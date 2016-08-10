from flask import jsonify
from flask_login import current_user


def get_user_info():
    response = {}
    response['isAuthenticated'] = current_user.is_authenticated
    if current_user.is_authenticated:
        response['name'] = current_user.name

    return jsonify(response)
