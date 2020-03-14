from flask import Blueprint

api = Blueprint(__name__, "api")


@api.route("/")
def index():
    return "Index", 200
