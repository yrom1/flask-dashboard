from urllib.parse import urlparse
import requests


def csv_static(url: str) -> str:
    """Save csv in flask static folder, return path to csv.

    >>> https://raw.githubusercontent.com/yrom1/jira-python/main/plot.csv
    /static/yrom1-jira-python-main-plot.csv
    """
    path = "./static/" + urlparse(url).path[1:].replace("/", "-")
    with open(path, "w") as f:
        f.write(requests.get(url).text)
    return path


csv_static("https://raw.githubusercontent.com/yrom1/jira-python/main/plot.csv")
