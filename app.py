# save this as app.py
from flask import Flask
from markupsafe import escape
from flask import url_for
from flask import render_template
from markupsafe import Markup

app = Flask(__name__)


# @app.route("/hello/")
# @app.route("/hello/<name>")
# def hello(name=None):
#     return render_template("hello.html", name=name)


@app.route("/")
@app.route("/<page>")
def hello(page=None):
    if page == "test":
        content = Markup("<h1>TEST TEST TEST</h1>")
    else:
        content = "Hi!"
    return render_template("layout.html", content=content)
