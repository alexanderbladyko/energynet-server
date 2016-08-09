from flask import request, jsonify, abort
from flask_login import current_user

from auth.models import User
from base.exceptions import EnergynetException


def register():
    if request.method == 'POST':
        if current_user.is_authenticated:
            abort(400)

        data = dict(request.form)

        name = data['username'][0]
        raw_password = data['password'][0]

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
