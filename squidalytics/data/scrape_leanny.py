import json

import requests
from bs4 import BeautifulSoup

RAW_URL = "https://raw.githubusercontent.com/"
VERSION_URL = (
    "https://github.com/Leanny/leanny.github.io/tree/master/splat3/data/mush"
)
LANG_URL = "Leanny/leanny.github.io/master/splat3/data/language/USen.json"


def get_latest_version_url() -> str:
    page = requests.get(VERSION_URL)
    soup = BeautifulSoup(page.content, "html.parser")
    versions = soup.find_all("a", class_="js-navigation-open Link--primary")
    versions_text = [(version.text, i) for i, version in enumerate(versions)]
    versions_text.sort(key=lambda x: x[0])
    latest_version_idx = versions_text[-1][1]
    latest_version = versions[latest_version_idx]
    out_url: str = RAW_URL + latest_version["href"]
    out_url = out_url.replace("/tree", "")
    return out_url


def get_weapon_data() -> dict:
    url = get_latest_version_url() + "/WeaponInfoMain.json"
    page = requests.get(url)
    json_data = json.loads(page.content)
    return json_data


def get_language_data() -> dict:
    page = requests.get(RAW_URL + LANG_URL)
    json_data = json.loads(page.content)
    return json_data


def localize(language_data: dict, key: str) -> str:
    # Try each of the possible keys in order.
    MAIN_KEY = "CommonMsg/Weapon/WeaponName_Main"
    SUB_KEY = "CommonMsg/Weapon/WeaponName_Sub"
    SPECIAL_KEY = "CommonMsg/Weapon/WeaponName_Special"
    try:
        return language_data[MAIN_KEY][key]
    except KeyError:
        pass
    try:
        return language_data[SUB_KEY][key]
    except KeyError:
        pass
    return language_data[SPECIAL_KEY][key]
