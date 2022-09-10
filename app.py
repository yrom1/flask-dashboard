# save this as app.py
from flask import Flask
from markupsafe import escape
from flask import url_for
from flask import render_template

app = Flask(__name__)


# @app.route("/hello/")
# @app.route("/hello/<name>")
# def hello(name=None):
#     return render_template("hello.html", name=name)


@app.route("/")
def hello(page=None):
    return render_template("layout.html", page=page)
