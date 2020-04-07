from flask import Blueprint, render_template

site = Blueprint("site", __name__)


@site.route('/', methods=['GET'])
def index():
    return render_template("index.html"), 200
