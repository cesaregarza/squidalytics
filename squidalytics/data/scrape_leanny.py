import json
import re
from typing import TypeAlias

import requests
from bs4 import BeautifulSoup

RAW_URL = "https://raw.githubusercontent.com/"
VERSION_URL = (
    "https://github.com/Leanny/leanny.github.io/tree/master/splat3/data/mush"
)
LANG_URL = "Leanny/leanny.github.io/master/splat3/data/language/USen.json"

WeaponsMap: TypeAlias = dict[str, dict[str, str | float]]


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


def get_versus_weapons() -> list[dict]:
    weapon_data = get_weapon_data()
    return [x for x in weapon_data if x.get("Type", None) == "Versus"]


def get_coop_weapons() -> list[dict]:
    weapon_data = get_weapon_data()
    return [x for x in weapon_data if x.get("Type", None) == "Coop"]


def map_localized_names(weapon_data: list[dict]) -> list[dict]:
    language_data = get_language_data()
    special_regex = re.compile(
        r"(?<=Work\/Gyml\/).*(?=\.spl__WeaponInfoSpecial\.gyml)"
    )
    sub_regex = re.compile(r"(?<=Work\/Gyml\/).*(?=\.spl__WeaponInfoSub\.gyml)")
    for weapon in weapon_data:
        weapon["Name"] = localize(language_data, weapon["__RowId"])
        special = special_regex.search(weapon["SpecialWeapon"]).group(0)
        sub = sub_regex.search(weapon["SubWeapon"]).group(0)
        weapon["Special"] = localize(language_data, special)
        weapon["Sub"] = localize(language_data, sub)

    return weapon_data


def get_versus_weapons_simplified() -> WeaponsMap:
    full_list = map_localized_names(get_versus_weapons())
    out = {}
    for weapon in full_list:
        dic = {
            k: v
            for k, v in weapon.items()
            if k in ["Name", "Special", "Sub", "Range", "SpecialPoint"]
        }
        out[dic["Name"]] = dic
    return out
