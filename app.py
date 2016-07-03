from flask import Flask, request
from flask.ext.login import LoginManager, LoginForm, next_is_valid
from gevent import monkey

from helpers.redis import redis

monkey.patch_all()

app = Flask(__name__)
login_manager = LoginManager()

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return {
        'id': id,
    }


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        next = request.args.get('next')

        if not next_is_valid(next):
            return Flask.abort(400)

        return Flask.redirect(next or Flask.url_for('index'))
    return 'login_form'


@app.route('/')
def main():
    redis.incr('test')
    return 'test'


if __name__ == '__main__':
    app.run()
