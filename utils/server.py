from flask import Flask

from utils.config import config


app = Flask(__name__)
app.config['SECRET_KEY'] = config.get('socketio', 'secret')
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
app.debug = config.get('app', 'debug')
