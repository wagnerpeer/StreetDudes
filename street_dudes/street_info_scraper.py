from functools import wraps
import inspect
import urllib.parse

import bs4
import requests
from requests.compat import urljoin


def get_strschl_href(session):
    response = session.get(
        session.with_base_url("/geodatenportal/"), params={"p": "strassen"}
    )

    if response:
        site = bs4.BeautifulSoup(response.text, "html.parser")
        href = site.find(
            "a", title="Straßenverzeichnis als .csv-Datei herunterladen"
        ).get("href")

        return href


def get_streets(link_to_streets, session):
    response = session.get(session.with_base_url(link_to_streets))

    if response:
        data = response.text.split("\r\n")
        copyright, header, lines = data[0], data[1], data[2:-1]

        streets_data = []
        for line in lines:
            street_name, strschl = line.split(";")
            streets_data.append({"street_name": street_name, "strschl": strschl})

        return streets_data


def post(strschl, session):
    data = {"strschl": strschl}

    response = session.post(
        session.with_base_url("/stadtplan/php/hsnr_info.php"), data=data
    )

    if response:
        soup = bs4.BeautifulSoup(response.text)

        print()
        print(soup.prettify)
        print()


if __name__ == "__main__":
    base_url = "http://geo.osnabrueck.de"
    session = requests.Session()
    session.with_base_url = lambda path: urllib.parse.urljoin(base_url, path)

    link_to_streets = get_strschl_href(session)
    streets = get_streets(link_to_streets, session)
    for street in streets:
        post(street["strschl"], session=session)
