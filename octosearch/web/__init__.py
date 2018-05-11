from flask import Flask
from .. import config

conf = None
app = Flask(__name__)

# not at top of file because `app` had to be initialized first
from . import views


def configure(config):
    global conf

    conf = config
    app.secret_key = conf.get('web', 'secret-key')
