from flask import Blueprint, jsonify

api = Blueprint(__name__, "api")


@api.route("/")
def index():
    return "Index", 200
