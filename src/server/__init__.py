from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from . import config

app = Flask(__name__)
app.config.from_object(config.Config)
db = SQLAlchemy(app)

from .models import *

from .api.routes import api

app.register_blueprint(api)
