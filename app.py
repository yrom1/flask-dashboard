# save this as app.py
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from zoneinfo import ZoneInfo

import requests
import simplejson
from bs4 import BeautifulSoup as bs
from cloud_dictionary import Cloud
from markdown_code_blocks import highlight
from markupsafe import Markup, escape

from flask import Flask, render_template, send_from_directory, url_for

DYNAMODICT = Cloud("plotsV2")
app = Flask(__name__)

# https://clrs.cc/
GREEN = "#2ECC40"
YELLOW = "#FFDC00"
RED = "#FF4136"


def jira_color() -> str:
    ISSUES_DONE_TODAY = int(Cloud("kpiV1")["ISSUES_DONE_TODAY"])
    if ISSUES_DONE_TODAY <= 2:
        return RED
    elif ISSUES_DONE_TODAY > 2 and ISSUES_DONE_TODAY <= 3:
        return YELLOW
    else:
        return GREEN


def leetcode_color() -> str:
    QUESTIONS_DONE_PAST_WEEK = int(Cloud("kpiV1")["QUESTIONS_DONE_PAST_WEEK"])
    if QUESTIONS_DONE_PAST_WEEK >= 7:
        return GREEN
    elif QUESTIONS_DONE_PAST_WEEK >= 4 and QUESTIONS_DONE_PAST_WEEK < 7:
        return YELLOW
    else:
        return RED


def strava_color() -> str:
    DAYS_SINCE_LAST_RUN = int(Cloud("kpiV1")["DAYS_SINCE_LAST_RUN"])
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
        jira_json=clean_json(mp["jira"]),
        leetcode_json=clean_json(mp["leetcode"]),
        strava_json=clean_json(mp["strava"]),
        dashboard=dashboard,
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


def ISSUES_DONE_THIS_MONTH():
    return int(mp["ISSUES_DONE_THIS_MONTH"])


def LEETCODE_QUESTIONS_THIS_MONTH():
    return int(mp["LEETCODE_QUESTIONS_THIS_MONTH"])


def KMS_RAN_THIS_MONTH():
    return int(mp["KMS_RAN_THIS_MONTH"])


def per_day(metric):
    DAY_OF_MONTH = datetime.now(ZoneInfo("US/Eastern")).date().day
    return round(metric / DAY_OF_MONTH)


space = " " * 2


@app.route("/dashboard")
def dashboard() -> str:
    return render(
        dedent(
            f"""\
        <p align="center">This page automatically refreshes every 5 minutes to update the dashboard.</p>
        <h1 id="Dashboard">Personal dashboard</h1>
        <table style="width:100%">
            <tr>
                <th style="text-align:left" colspan="3"><b><i>This month —</i></b></th>
            </tr>
            <tr class="metrics">
                <td>Issues Completed</td>
                <td>LeetCode Questions</td>
                <td>Kilometers Ran</td>
            </tr>
            <tr class="numbers">
                <td><strong>{ISSUES_DONE_THIS_MONTH()}</strong><span class="day">{space}({per_day(ISSUES_DONE_THIS_MONTH())}/day)</span></td>
                <td><strong>{LEETCODE_QUESTIONS_THIS_MONTH()}</strong><span class="day">{space}({per_day(LEETCODE_QUESTIONS_THIS_MONTH())}/day)</span></td>
                <td><strong>{KMS_RAN_THIS_MONTH()}</strong><span class="day">{space}({per_day(KMS_RAN_THIS_MONTH())}/day)</span></td>
            </tr>
        </table>
        <table style="width:100%">
            <tr>
                <th style="text-align:left"><i>Overview —</i></th>
                <th width="10%">Status</th>
            </tr>
            <tr align="center">
                <td><div id="jira"></div></td>
                <td style="background-color:{jira_color()}"></td>
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
        <blockquote><p>With computers available, it is a waste to perform calculations by hand.</p></blockquote><figcaption>—Taiichi Ohno, <cite class="cite">Toyota Production System Beyond Large-Scale Production</cite></figcaption>
        <h2>Dashboard explanation</h2>
        <p>This dashboard tracks some useful KPIs about myself, specifically:</p>
        <ul>
            <li>The first graph is about Jira, issue tracking software. I find it helpful to see how much effort I've been exerting recently, measured by the number of Jira issues completed, i.e. put in the 'Done' column of a Jira kanban board.</li>
            <li>The middle graph pertains to LeetCode, a programming practice problem site. Knowing how many questions I've done the past week is helpful to see if I'm hitting my desired pace. It helps me choose if I should practice Python or SQL on a given day. And seeing my progress over a long period of time is good motivation.</li>
            <li>The last graph pertains to Strava, a GPS run tracking app. I find this graph particularly useful to know how many days it's been since I ran last, which is an easy thing to forget. Also, it's helpful to see the distance I ran, to see if I'm making any progress.</li>
        </ul>
        <p>The <a href="https://en.wikipedia.org/wiki/Andon_(manufacturing)">andon</a> colors let me know if my desired pace is being achieved (in the S.M.A.R.<strong>T.</strong> sense).
        <h2>Source code</h2>
        <p>The general idea for this dashboard is about using Github Actions to run Python scripts to update the graph image files and KPIs such as 'DAYS_SINCE_LAST_RUN', which I store in public Github repositories. If needed data is scraped and stored in a SQLite database, this is only needed for the LeetCode metrics as Jira and Strava store the data for me. Based on the KPIs the andon green-yellow-red colors are updated every time the page is refreshed by Flask. The KPIs themselves are stored as plain text in the relevant Github repositories.</p>

        <p>
            Relevant source code repos: <a href="https://github.com/yrom1/jira-python">Jira</a>, <a href="https://github.com/yrom1/yrom1">LeetCode</a>, <a href="https://github.com/yrom1/strava-rest">Strava</a>, <a href="https://github.com/yrom1/flask">this Flask website</a>, the <a href="https://github.com/yrom1/opengraph-preview">Open Graph dynamic preview image</a> and an <a href="https://github.com/yrom1/sqlite-etl">ETL repo</a> used when I switched from a flat-file database to a SQLite database.
        </p>

        <p>
        <b>UPDATE</b> (14 Sep 2022): I switched from Matplotlib to Plotly.js. The main motivation was to make the graphs responsive to screen size changes. Another problem I was having using Matplotlib image files stored in different repositories, was that it combined data and styling. Now each repository provides <i>only</i> a single data file for plotting, 'plot.json', and all the stying code is contained in this repository in JavaScript.
        <p>

        <p>
        <b>UPDATE</b> (17 Sep 2022): Now the 'plot.json' and KPI values are stored in DynamoDB tables. This should make adding new metrics or plots much easier. I also made <a href="https://pypi.org/project/cloud-dictionary/">cloud-dictionary</a>, which is a small wrapper around boto3's DynamoDB interface to make the database act like a Python dictionary by implementing the MutableMapping abstract base class. One of the trickier parts was figuring out how to get Flask to render JSON data into the front-end JavaScript, but it's actually quite easy once you find the right part of the documentation. Oh, and I added light and dark themes using the in-browser JavaScript window object's 'prefers-color-scheme', always wondered how that worked.
        <p>
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
        title="Ryan | dashboard",
        dashboard=True,
    )

import subprocess

def repo_description(project: str) -> str:
    cmd = f"curl -s https://github.com/yrom1/{project} | grep \/title"
    x = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode('utf-8').split(':')[1].strip()
    return x[:x.find('<')]

@app.route("/projects")
def projects():
    project_names = [
        'cloud-dictionary',
        'mypandas',
        'ty',
        'exception-logging',
        'postgrespy',
    ]
    projects = {
        name: {
            'readme': f"https://raw.githubusercontent.com/yrom1/{name}/main/README.md",
            'tagline': repo_description(name),
        }
     for name in project_names}
    ans = ""
    for project in projects:
        ans += '<h3 style="text-align: left;">' + project + '</h3>' + f'<p>{projects[project]["tagline"]}</p>'
    ans += '<hr>'
    ans += '<hr>'.join([markdown_readme_to_html(projects[project]['readme']) for project in projects])
    return render(
        ans,
        title="Ryan | projects",
    )
