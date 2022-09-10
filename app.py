# save this as app.py
from textwrap import dedent

import requests
from bs4 import BeautifulSoup as bs
from markdown_code_blocks import highlight
from markupsafe import Markup, escape

from flask import Flask, render_template, url_for

app = Flask(__name__)

# https://clrs.cc/
GREEN = "#2ECC40"
YELLOW = "#FFDC00"
RED = "#FF4136"


def jira_color() -> str:
    ISSUES_DONE_TODAY = int(
        requests.get(
            "https://raw.githubusercontent.com/yrom1/jira-python/main/ISSUES_DONE_TODAY"
        ).text
    )
    if ISSUES_DONE_TODAY <= 2:
        return RED
    elif ISSUES_DONE_TODAY > 2 and ISSUES_DONE_TODAY <= 3:
        return YELLOW
    else:
        return GREEN


def leetcode_color() -> str:
    QUESTIONS_DONE_PAST_WEEK = int(
        requests.get(
            "https://raw.githubusercontent.com/yrom1/yrom1/main/QUESTIONS_DONE_PAST_WEEK"
        ).text
    )
    if QUESTIONS_DONE_PAST_WEEK >= 7:
        return GREEN
    elif QUESTIONS_DONE_PAST_WEEK >= 4 and QUESTIONS_DONE_PAST_WEEK < 7:
        return YELLOW
    else:
        return RED


def strava_color() -> str:
    DAYS_SINCE_LAST_RUN = int(
        requests.get(
            "https://raw.githubusercontent.com/yrom1/strava-rest/main/DAYS_SINCE_LAST_RUN"
        ).text
    )
    if DAYS_SINCE_LAST_RUN <= 1:
        return GREEN
    elif DAYS_SINCE_LAST_RUN > 1 and DAYS_SINCE_LAST_RUN <= 2:
        return YELLOW
    else:
        return RED


def markdown_readme_to_html(url: str) -> str:
    r = requests.get(url)
    assert r.status_code == 200
    ty_markdown = r.text
    html = highlight(ty_markdown)
    return html


def render(content, *, head=""):
    # NOTE Must trust content!
    return render_template(
        "layout.html",
        content=Markup(bs(content, features="lxml").prettify()),
        head=Markup(head),
    )


# @app.route("/")
# TODO ?


@app.route("/")
def index() -> str:
    return render(
        "Redirecting to dashboard!",
        head=dedent(
            """
        <meta http-equiv="refresh" content="2; url=/dashboard" />
        """
        ),
    )


@app.route("/about")
def about() -> str:
    return render(
        """
    <h1>About me</h1>
    <ul>
        <li>2+ years of paid experience coding</li>
        <li>Strong Python and SQL skills</li>
        <li>Engineering master's degree</li>
    </ul>
    <p>Feel free to email me. A resume can be provided on request.</p>
    """
    )


@app.route("/dashboard")
def dashboard() -> str:
    return render(
        dedent(
            f"""\
        <h1 id="Dashboard">Personal dashboard</h1>
        <p align="center">This page automatically refreshes every 5 minutes to update the dashboard.</p>
        <table style="width:100%">
            <tr>
                <th></th>
                <th><a href="https://en.wikipedia.org/wiki/Andon_(manufacturing)">Andon</a></th>
            </tr>
            <tr align="center">
                <td><img src="https://raw.githubusercontent.com/yrom1/jira-python/main/Jira_hustle_graph.png"/></td>
                <td style="background-color:{jira_color()};">&nbsp;&nbsp;&nbsp;&nbsp;</td>
            </tr>
            <tr align="center">
                <td><img src="https://raw.githubusercontent.com/yrom1/yrom1/main/LeetCode_graph.png"/></td>
                <td style="background-color:{leetcode_color()};"></td>
            </tr>
            <tr align="center">
                <td><img src="https://raw.githubusercontent.com/yrom1/strava-rest/main/Strava_run_graph.png"/></td>
                <td style="background-color:{strava_color()};"></td>
            </tr>
        </table>
        <blockquote><p>With computers available, it is a waste to perform calculations by hand.</p></blockquote><figcaption>—Taiichi Ohno, <cite class="cite">Toyota Production System Beyond Large-Scale Production</cite></figcaption>
        <h2>Dashboard explanation</h2>
        <p>This dashboard tracks some useful metrics about myself, specifically:</p>
        <ul>
            <li>The first graph is about Jira, issue tracking software. I find it helpful to see how much effort I've been exerting recently, measured by the number of Jira issues completed, i.e. put in the 'Done' column of a Jira kanban board.</li>
            <li>The middle graph pertains to LeetCode, a programming practice problem site. Knowing how many questions I've done the past week is helpful to see if I'm hitting my desired pace. It helps me choose if I should practice Python or SQL on a given day. And seeing my progress over a long period of time is good motivation.</li>
            <li>The last graph pertains to Strava, a GPS run tracking app. I find this graph particularly useful to know how many days it's been since I ran last, which is an easy thing to forget. Also, it's helpful to see the distance I ran, to see if I'm making any progress.</li>
        </ul>
        <h2>Source code</h2>
        The general idea for this dashboard is about using Github Actions to run Python scripts to update these graph image files, and if needed gather data and store it in a SQLite database.
        <p>
            Relevant source code repos: <a href="https://github.com/yrom1/jira-python">Jira</a>, <a
                href="https://github.com/yrom1/yrom1">LeetCode</a>, <a
                href="https://github.com/yrom1/strava-rest">Strava</a> (a popular running app), <a
                href="https://github.com/yrom1/yrom1.github.io">this website</a> and an <a
                href="https://github.com/yrom1/sqlite-etl">ETL repo</a> used when I switched from a flat-file database to a SQLite database.
        </p>\
        """
        ),
        head=dedent(
            """
            <style>
                img {
                    width: 100%;
                }
            </style>
        """
        ),
    )


@app.route("/mypandas")
def mypandas() -> str:
    url = "https://raw.githubusercontent.com/yrom1/mypandas/main/README.md"
    return render(markdown_readme_to_html(url))


@app.route("/ty")
def ty() -> str:
    url = "https://raw.githubusercontent.com/yrom1/ty/main/README.md"
    return render(markdown_readme_to_html(url))


@app.route("/exlog")
def exlog() -> str:
    url = "https://raw.githubusercontent.com/yrom1/exception-logging/main/README.md"
    return render(markdown_readme_to_html(url))


@app.route("/postgrespy")
def postgrespy() -> str:
    url = "https://raw.githubusercontent.com/yrom1/postgrespy/main/README.md"
    return render(markdown_readme_to_html(url))


@app.route("/fun")
def fun() -> str:
    return render(
        "<hr>".join(
            [
                """
    <h1>Etch a sketch</h1>
    <!-- ETCH-A-SKETCH  -->
    <p>Move your mouse around in the box!</p>
    <div id="container"></div>

    <form id="etch-form">
        <button type="submit">reset</button><br>
        <label for="fun-check">fun</label>
        <input type="checkbox" name="fun-check"></input>
    </form>

    <form id="etch-fun-form">
    </form>

    <script src="/static/etch.js"></script>
    <!-- --- -->
    <p>I made this as part of <a href="https://www.theodinproject.com/">The Odin Project</a> when I was thinking of becoming a front-end developer.</p>
    """,
                """<h1>Python3 Metaprogramming</h1>
    <iframe width="560" height="315" src="https://www.youtube.com/embed/sPiWg5jSoZI" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    <p>This is a wonderful talk by <a href="https://en.wikipedia.org/wiki/David_M._Beazley">David Beazley</a>, and despite being a very old talk is still up to date because it was about an early version of Python3 at the time. One of the exercises left to the reader in this tutorial is to make a class decorator that works with <code>@staticmethod</code>s, and <code>@classmethod</code>s, something that you actually don't see a lot. And that challenge was what inspired me to make my exception logging package on PyPI (<a href="https://pypi.org/project/exlog/">exlog</a>). And I'm glad I did, because otherwise I wouldn't of understood why class decorators and metaclasses work together so seamlessly.</p>
    """,
                """
    <h1>CMU 15-445/645</h1>
    <p>A <a href="https://15445.courses.cs.cmu.edu/fall2019/">great database course</a> is given by <a href="https://twitter.com/andy_pavlo">Andy Pavlo</a>, who is objectively hilarious. His course begins by him presenting from his bathtub during COVID:</p>
    <iframe width="560" height="315" src="https://www.youtube.com/embed/videoseries?list=PLSE8ODhjZXjbohkNBWQs_otTrBTrjyohi" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    <p>I would give two downsides about auditing this course, which I should note I thought was otherwise very excellent:</p>
    <ul>
        <li>The C++ assignments are checked for correctness using an internal system (BusTub) that is unavailable to the public, which is slightly sad because they looked fun.</li>
        <li>While there are many time where Andy Pavlo goes out of his way to show differences in the behavior of different datebases (specifically MySQL, Postgres, and Oracle if I remember), which was often interesting and funny, at the end of the course I didn't feel like I a solid understanding of how exactly specific DBMSs worked internally.</li>
    </ul>
    As I'm not looking for a systems developer role any time soon, the first point isn't the end of the world. For the second point, and while it's just a start, an Uber Engineering blogpost '<a href="https://www.uber.com/en-CA/blog/postgres-to-mysql-migration/">Why Uber Engineering Switched from Postgres to MySQL</a>'...
    <img src="https://blog.uber-cdn.com/cdn-cgi/image/width=768,quality=80,onerror=redirect,format=auto/wp-content/uploads/2016/07/MySQL_Index_Property_Header.png">
    ... I felt did a solid job explaining some specific details about how MySQL and Postgres are implemented, particularily as it relates to indexes.
    """,
                """
    <h1>Dealing with Trolls</h1>
    <iframe width="560" height="315" src="https://www.youtube.com/embed/EBRMq2Ioxsc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    <p>I really like this keynote by <a href="https://en.wikipedia.org/wiki/Guido_van_Rossum">Guido van Rossum</a>, it contextualizes a lot of the criticisms one hears about Python. Which for some reason online, are fairly common and widespread.</p>""",
            ]
        )
    )


if __name__ == "__app__":
    app.run(debug=False)
