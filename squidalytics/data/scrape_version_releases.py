from datetime import datetime, timezone
from functools import cache

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://splatoonwiki.org/wiki/List_of_updates_in_Splatoon_3"


@cache
def get_version_release_dates() -> dict[str, datetime]:
    """Get a dictionary of version release dates.

    Returns:
        dict[str, datetime]: A dictionary of version release dates.
    """
    page = requests.get(BASE_URL)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table", class_="wikitable")
    rows = table.find_all("tr")[1:]
    out = {}
    for row in rows:
        version = row.find("th").find("a").text
        date_str = row.find_all("td")[-1].find("span").get("title")
        date = datetime.strptime(date_str, "%Y-%m-%d")
        date = date.replace(tzinfo=timezone.utc)
        out[version] = date
    return out


def map_date_to_version(date: datetime) -> str:
    """Map a date to a version.

    Args:
        date (datetime): The date to map to a version.

    Returns:
        str: The version.
    """
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    version_dates = get_version_release_dates()
    version_dates = {k: v for k, v in version_dates.items() if v < date}
    version_dates = sorted(version_dates.items(), key=lambda x: x[1])
    return version_dates[-1][0]
