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

application = Flask(__name__)
application.config.from_object(config.Config)
db = SQLAlchemy(application)

from .models import *

from .api.routes import api
from .site.routes import site

application.register_blueprint(api, url_prefix="/api")
application.register_blueprint(site)
