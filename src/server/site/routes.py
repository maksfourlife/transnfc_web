from . import site, render_template


@site.route('/', methods=['GET'])
def index():
    return render_template("index.html"), 200
