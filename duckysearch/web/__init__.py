from flask import Flask
from .. import config

app = Flask(__name__)
conf = config.Config()
app.secret_key = conf.get('web', 'secret-key')

from . import views
