from flask import request, jsonify, abort

from auth.models import User
from base.exceptions import EnergynetException


def register():
    if request.method == 'POST':
        auth_token = request.headers.get('Authorization')
        user_id = User.get_current_user_id(auth_token)
        if user_id is not None:
            abort(400)

        data = request.get_json()

        name = data['username']
        raw_password = data['password']

        try:
            User.create(name, raw_password)
        except EnergynetException as error:
            return jsonify({
                'success': False,
                'reason': error.message,
            }), 409

        return jsonify({
            'success': True,
        })
