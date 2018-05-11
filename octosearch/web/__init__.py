from flask import Flask
from .. import config

import os.path
import sys

app = Flask(__name__)

conf = config.Config(os.path.abspath(os.path.dirname(sys.argv[0])))
app.secret_key = conf.get('web', 'secret-key')

# not at top of file because `app` had to be initialized first
from . import views
