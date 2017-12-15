from flask import Flask
from .. import config

app = Flask(__name__)
conf = config.Config()
app.secret_key = conf.get('web', 'secret-key')


# not at top of file because `app` had to be initialized first
from . import views
