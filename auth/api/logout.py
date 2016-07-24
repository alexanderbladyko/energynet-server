from flask import jsonify
from flask_login import logout_user, login_required


@login_required
def logout():
    logout_user()
    return jsonify({
        'success': True,
    })
