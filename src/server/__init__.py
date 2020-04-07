from secrets import token_bytes


def generate_token(bytes_size=16):
    def normalize(s):
        s = s[2:]
        if len(s) == 1:
            s += '0'
        return s
    token = token_bytes(bytes_size)
    mod = round(datetime.now().timestamp() * 100) % 0xff
    return "".join(map(lambda x: normalize(hex(x ^ mod)), token))


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from . import config

app = Flask(__name__)
app.config.from_object(config.Config)
db = SQLAlchemy(app)

from .models import *

from .api.routes import api
from .site.routes import site

app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(site)
