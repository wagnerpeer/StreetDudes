import urllib.parse

import bs4
import requests


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
        _copyright, _header, lines = data[0], data[1], data[2:-1]

        streets_data = []
        for line in lines:
            street_name, strschl, *_ = line.split(";")
            streets_data.append({"street_name": street_name, "strschl": strschl})

        return streets_data


def parse_benennung_seit(strong_div):
    print(f"Benennung seit: {strong_div.parent.text}")


def parse_benannt_nach(strong_div):
    benannt_nach = strong_div.parent.next_sibling

    for br in benannt_nach.find_all("br"):
        br.replace_with("\n" + br.text)

    benannt_nach_lines = benannt_nach.text.split("\n")

    print(f"Benannt nach:{benannt_nach_lines}")


def parse_alte_strassenbezeichnung(strong_div):
    print(f"Alte Straßenbezeichnung: {strong_div.parent.text}")


def parse_hausnummern(hausnummer_divs):
    hausnummern = [hausnummer.text for hausnummer in hausnummer_divs]
    print(f"Hausnummern: {hausnummern}")


def post(street: dict[str, str], session):
    data = {"strschl": street["strschl"]}

    response = session.post(
        session.with_base_url("/stadtplan/php/hsnr_info.php"),
        data=data,
    )

    if response:
        soup = bs4.BeautifulSoup(response.text, features="html.parser")

        print(f"Straßenname: {street}", end="")
        print(street["street_name"])
        for strong_div in soup.find_all(["strong"]):
            if strong_div.text == "Benennung seit: ":
                parse_benennung_seit(strong_div)
            elif strong_div.text == "Benannt nach:":
                parse_benannt_nach(strong_div)
            elif strong_div.text == "Alte Straßenbezeichnung: ":
                parse_alte_strassenbezeichnung(strong_div)

        parse_hausnummern(soup.find_all("div", "hsnr cur_pointer"))


if __name__ == "__main__":
    print("Datenquelle/Source: 'dl-de/by-2-0: Stadt Osnabrück'")
    base_url = "https://geo.osnabrueck.de"
    session = requests.Session()
    session.with_base_url = lambda path: urllib.parse.urljoin(base_url, path)

    link_to_streets = get_strschl_href(session)
    streets = get_streets(link_to_streets, session)
    for street in streets:
        post(street, session=session)
