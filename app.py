# save this as app.py
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from random import choice
from textwrap import dedent
from zoneinfo import ZoneInfo

import requests
import simplejson
from bs4 import BeautifulSoup as bs
from cloud_dictionary import Cloud
from flask import Flask, render_template, send_from_directory, url_for
from markdown_code_blocks import highlight
from markupsafe import Markup, escape

DYNAMODICT = Cloud("plotsV2")
app = Flask(__name__)

# https://clrs.cc/
GREEN = "#2ECC40"
YELLOW = "#FFDC00"
RED = "#FF4136"
PURPLE = "#B10DC9"
TRANSPARENT = "#00FFFFFF"

def leetcode2_color() -> str:
    SUBMISSIONS = int(Cloud("kpiV1")["LEETCODE_SUBMISSIONS_THIS_WEEK"])
    if SUBMISSIONS >= 15:
        return GREEN
    elif SUBMISSIONS >= 5 and SUBMISSIONS < 15:
        return YELLOW
    else:
        return RED


def leetcode_color() -> str:
    # NOTE this is only questions that haven't been encountered before
    QUESTIONS_DONE_PAST_WEEK = int(Cloud("kpiV1")["QUESTIONS_DONE_PAST_WEEK"])
    if QUESTIONS_DONE_PAST_WEEK >= 2:
        return GREEN
    elif QUESTIONS_DONE_PAST_WEEK == 1:
        return YELLOW
    else:
        return RED


def strava_color() -> str:
    DAYS_SINCE_LAST_RUN = int(Cloud("kpiV1")["DAYS_SINCE_LAST_RUN"])
    if DAYS_SINCE_LAST_RUN <= 2:
        return GREEN
    elif DAYS_SINCE_LAST_RUN > 2 and DAYS_SINCE_LAST_RUN <= 4:
        return YELLOW
    else:
        return RED


def markdown_readme_to_html(url: str) -> str:
    r = requests.get(url)
    assert r.status_code == 200
    ty_markdown = r.text
    html = highlight(ty_markdown)
    return html


def clean_json(dict_):
    # clean the artifacts dynamodb caused
    ans = simplejson.dumps(dict_, use_decimal=True)
    return ans


def render(content, *, title="Ryan Moore", head="", dashboard=False):
    mp = Cloud("plotsV2")
    # NOTE Must trust content!
    return render_template(
        "layout.html",
        content=Markup(content),
        title=Markup(title),
        head=Markup(head),
        leetcode_json=clean_json(mp["leetcode"]),
        leetcode2_json=clean_json(mp["leetcode2"]),
        strava_json=clean_json(mp["strava"]),
        dashboard=dashboard,
        UNIX_TIMESTAMP=int(time.time()),
    )


@app.route("/")
def index() -> str:
    return render(
        "Redirecting to dashboard.",
        head=dedent(
            """
        <meta http-equiv="refresh" content="2; url=/dashboard" />
        """
        ),
    )


def kpi(url: str) -> int:
    return int(requests.get(url).text)


mp = Cloud("kpiV1")

def LEETCODE_SUBMISSIONS_THIS_MONTH() -> int:
    return sum(json.loads(Cloud("plotsV2")["leetcode2"])["leet_submission_counts"])

def ISSUES_DONE_THIS_MONTH():
    return int(mp["ISSUES_DONE_THIS_MONTH"])


def LEETCODE_QUESTIONS_THIS_MONTH():
    return int(mp["LEETCODE_QUESTIONS_THIS_MONTH"])


def KMS_RAN_THIS_MONTH():
    return int(mp["KMS_RAN_THIS_MONTH"])


def per_day(metric):
    DAY_OF_MONTH = datetime.now(ZoneInfo("US/Eastern")).date().day
    return round(metric / DAY_OF_MONTH)


class RandomQuote:
    def __init__(self):
        self._quotes = [
            # (quote, author, book)
            (
                "With computers available, it is a waste to perform calculations by hand.",
                "Taiichi Ohno",
                "Toyota Production System Beyond Large-Scale Production",
            ),
            (
                "The numbers have no way of speaking for themselves. We speak for them. We imbue them with meaning.",
                "Nate Silver",
                "The Signal and the Noise",
            ),
        ]
        for quote in self._quotes:
            assert len(quote) == 3
        self._index = choice(range(len(self._quotes)))

    @property
    def quote(self):
        return self._quotes[self._index][0]

    @property
    def author(self):
        return self._quotes[self._index][1]

    @property
    def book(self):
        return self._quotes[self._index][2]


space = " " * 2


@app.route("/dashboard")
def dashboard() -> str:
    quote = RandomQuote()
    return render(
        dedent(
            f"""\
        <h1 id="Dashboard">Personal Dashboard</h1>
        <table style="width:100%">
            <tr>
                <th style="text-align:left" colspan="3"><b><i>This Month ???</i></b></th>
            </tr>
            <tr class="metrics">
                <td>LC Submissions</td>
                <td>New LC Questions</td>
                <td>Kilometers Ran</td>
            </tr>
            <tr class="numbers">
                <td><strong>{LEETCODE_SUBMISSIONS_THIS_MONTH()}</strong><span class="day">{space}({per_day(LEETCODE_SUBMISSIONS_THIS_MONTH())}/day)</span></td>
                <td><strong>{LEETCODE_QUESTIONS_THIS_MONTH()}</strong><span class="day">{space}({per_day(LEETCODE_QUESTIONS_THIS_MONTH())}/day)</span></td>
                <td><strong>{KMS_RAN_THIS_MONTH()}</strong><span class="day">{space}({per_day(KMS_RAN_THIS_MONTH())}/day)</span></td>
            </tr>
        </table>
        <table style="width:100%">
            <tr>
                <th style="text-align:left"><i>Overview ???</i></th>
                <th width="10%">Status</th>
            </tr>
            <tr align="center">
                <td><div id="leetcode2"></div></td>
                <td style="background-color:{leetcode2_color()};"></td>
            </tr>
            <tr align="center">
                <td><div id="leetcode"></div></td>
                <td style="background-color:{leetcode_color()};"></td>
            </tr>
            <tr align="center">
                <td><div id="strava"></div></td>
                <td style="background-color:{strava_color()};"></td>
            </tr>
        </table>
        <blockquote><p>{quote.quote}</p></blockquote><figcaption>???{quote.author}, <cite class="cite">{quote.book}</cite></figcaption>
        <h2>Dashboard Explanation</h2>
        <p>This dashboard tracks some useful KPIs about myself, specifically:</p>
        <ul>
            <li>The first two graphs pertains to LeetCode, a programming practice problem site. The number of submissions, which is a rough measure of my activity attempting questions, and number of new questions completed.</li>
            <li>The last graph pertains to Strava, a GPS run tracking app. I find this graph particularly useful to know how many days it's been since I ran last, which is an easy thing to forget.</li>
        </ul>
        <p>The <a href="https://en.wikipedia.org/wiki/Andon_(manufacturing)">andon</a> colors let me know if my desired pace is being achieved (in the S.M.A.R.<strong>T.</strong> sense).
        <h2>Source code</h2>
        <p>The general idea for this dashboard is about using GitHub Actions to run Python scripts to update the graph image files and KPIs such as 'DAYS_SINCE_LAST_RUN', which I store in public GitHub repositories. If needed data is scraped and stored in a SQLite database, this is only needed for the LeetCode metrics as Jira and Strava store the data for me. Based on the KPIs the andon green-yellow-red colors are updated every time the page is refreshed by Flask. The KPIs themselves are stored as plain text in the relevant GitHub repositories.</p>

        <p>
            Relevant source code repos: <a href="https://github.com/yrom1/jira-python">Jira</a>, <a href="https://github.com/yrom1/yrom1">LeetCode</a>, <a href="https://github.com/yrom1/strava-rest">Strava</a>, <a href="https://github.com/yrom1/flask">this Flask website</a> and an <a href="https://github.com/yrom1/sqlite-etl">ETL repo</a> used when I switched from a flat-file database to a SQLite database.
        </p>

        <p>
        <b>UPDATE</b> (14 Sep 2022): I switched from Matplotlib to Plotly.js. The main motivation was to make the graphs responsive to screen size changes. Another problem I was having using Matplotlib image files stored in different repositories, was that it combined data and styling. Now each repository provides <i>only</i> a single data file for plotting, 'plot.json', and all the stying code is contained in this repository in JavaScript.
        <p>

        <p>
        <b>UPDATE</b> (17 Sep 2022): Now the 'plot.json' and KPI values are stored in DynamoDB tables. This should make adding new metrics or plots much easier. I also made <a href="https://pypi.org/project/cloud-dictionary/">cloud-dictionary</a>, which is a small wrapper around boto3's DynamoDB interface to make the database act like a Python dictionary by implementing the MutableMapping abstract base class. One of the trickier parts was figuring out how to get Flask to render JSON data into the front-end JavaScript, but it's actually quite easy once you find the right part of the documentation. Oh, and I added light and dark themes using the in-browser JavaScript window object's 'prefers-color-scheme', always wondered how that worked.
        <p>

        <p>
        <b>UPDATE</b> (24 Sep 2022): I've set up a small data warehouse on Amazon RDS. The motivation is I want to make a monthly overview dot plot, showing how I did each day of the month by the color of the dots, so I'll need to save historical data. I decided on a <a href="https://github.com/yrom1/star-schema">star-schema</a>, where the fact table stores daily snapshots of various metrics. I used Git submodules to share the star-schema code with the metric tracking repositories, and I also used a symbolic link to hoist the submodules main Python file into the host repository (so it could be imported in Python). In the future, I'll probably make the star-schema submodule pip installable (for local use not on PyPI), so you don't need to manually copy and paste things like the submodule's dependencies.
        </p>
        <p>
        At this point, the website works as follows: GitHub Action tracker repositories generate -> Daily metrics data -> Stored in an Amazon RDS star schema -> Queried to create KPIs and JSON plot data -> Stored in DynamoDB tables -> Flask uses to fill in HTML templates -> Plots generated in the browser by Plotly.js!
        </p>
        <p>
        <b>UPDATE</b> (6 Dec 2022): RIP Jira Tracker.
        </p>
        <p>
        <b>UPDATE</b> (8 Dec 2022): Added a plot for LeetCode submissions, the color is purple because I don't know what to expect for it in terms of what is good or bad.
        </p>
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
        title="Ryan | Dashboard",
        dashboard=True,
    )


def repo_description(project: str) -> str:
    cmd = f"curl -s https://github.com/yrom1/{project} | grep /title"
    x = (
        subprocess.run(cmd, shell=True, capture_output=True)
        .stdout.decode("utf-8")
        .split(":")[1]
        .strip()
    )
    return x[: x.find("<")]


@app.route("/projects")
def projects():
    project_names = [
        "cloud-dictionary",
        "mypandas",
        "ty-command",
        "exception-logging",
        "postgrespy",
    ]
    projects = {
        name: {
            "readme": f"https://raw.githubusercontent.com/yrom1/{name}/main/README.md",
            "tagline": repo_description(name),
        }
        for name in project_names
    }
    ans = ""
    for project in projects:
        ans += (
            f'<h3 style="text-align: left;"><a href="#{project}">'
            + project
            + "</a></h3>"
            + f'<p>{projects[project]["tagline"]}</p>'
        )
    ans += "<hr>"
    ans += "<hr>".join(
        [
            # a lil hacky to get hyperlinks to titles
            # depends on first line of every readme being a title which can replace
            f'<a href="#">???</a><h1 id="{project}">{project} ??? <a href="https://github.com/yrom1/{project}" target="_blank">source</a></h1>'
            + "\n".join(
                markdown_readme_to_html(projects[project]["readme"]).splitlines()[1:]
            )
            for project in projects
        ]
    )
    return render(
        ans,
        title="Ryan | Projects",
    )
