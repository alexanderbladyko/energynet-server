from flask import jsonify


def logout():
    return jsonify({
        'success': True,
    })
