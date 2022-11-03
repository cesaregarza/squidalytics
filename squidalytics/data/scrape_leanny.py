import json
import re
from typing import TypeAlias

import requests
from bs4 import BeautifulSoup

RAW_URL = "https://raw.githubusercontent.com/"
VERSION_URL = (
    "https://github.com/Leanny/leanny.github.io/tree/master/splat3/data/mush"
)
LANG_URL = "Leanny/leanny.github.io/master/splat3/data/language/"

WeaponsMap: TypeAlias = dict[str, dict[str, str | float]]


def get_version_url(version: str | None = None) -> str:
    """Get the URL for the specified version of the datamine. If no version is
    specified, get the latest version.

    Args:
        version (str | None): The version to get the URL for. If None, get the
            latest version. Defaults to None.

    Returns:
        str: The URL for the specified version.
    """
    page = requests.get(VERSION_URL)
    soup = BeautifulSoup(page.content, "html.parser")
    versions = soup.find_all("a", class_="js-navigation-open Link--primary")
    versions_text = [(version.text, i) for i, version in enumerate(versions)]
    if version is None:
        versions_text.sort(key=lambda x: x[0])
        selected_version_idx = versions_text[-1][1]
    else:
        version = version.replace("v", "").replace(".", "")
        selected_version_idx = [x[1] for x in versions_text if x[0] == version][
            0
        ]
    selected_version_soup = versions[selected_version_idx]
    out_url: str = RAW_URL + selected_version_soup["href"]
    out_url = out_url.replace("/tree", "")
    return out_url


def get_weapon_data(version: str | None = None) -> dict:
    """Get the weapon data from the specified version of the datamine. If no
    version is specified, get the latest version.

    Args:
        version (str | None): The version to get the data from. If None, get the
            latest version. Defaults to None.

    Returns:
        dict: The weapon data.
    """
    url = get_version_url(version=version) + "/WeaponInfoMain.json"
    page = requests.get(url)
    json_data = json.loads(page.content)
    return json_data


def get_language_data(lang: str = "USen") -> dict:
    """Get the language data for the specified language.

    Args:
        lang (str): The language to get the data for. Defaults to "USen".

    Returns:
        dict: The language data.
    """
    page = requests.get(RAW_URL + LANG_URL + lang + ".json")
    json_data = json.loads(page.content)
    return json_data


def localize(language_data: dict, key: str) -> str:
    """Get the localized name for the specified key.

    Args:
        language_data (dict): The language data, loaded from a JSON file.
        key (str): The key to get the localized name for.

    Returns:
        str: The localized name.
    """
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


def get_versus_weapons(version: str | None = None) -> list[dict]:
    """Get the versus weapons from the specified version of the datamine. If no
    version is specified, get the latest version.

    Args:
        version (str | None): The version to get the data from. If None, get the
            latest version. Defaults to None.

    Returns:
        list[dict]: The versus weapons.
    """
    weapon_data = get_weapon_data(version=version)
    return [x for x in weapon_data if x.get("Type", None) == "Versus"]


def get_coop_weapons(version: str | None = None) -> list[dict]:
    """Get the co-op weapons from the specified version of the datamine. If no
    version is specified, get the latest version.

    Args:
        version (str | None): The version to get the data from. If None, get the
            latest version. Defaults to None.

    Returns:
        list[dict]: The co-op weapons.
    """
    weapon_data = get_weapon_data(version=version)
    return [x for x in weapon_data if x.get("Type", None) == "Coop"]


def map_localized_names(
    weapon_data: list[dict[str, str]], lang: str = "USen"
) -> list[dict]:
    """Map the localized names for the specified weapons.

    Args:
        weapon_data (list[dict[str, str]]): The weapon data, loaded from the
            datamine.
        lang (str): The language to use. Defaults to "USen".

    Returns:
        list[dict]: The weapon data with localized names.
    """
    language_data = get_language_data(lang=lang)
    special_regex = re.compile(
        r"(?<=Work\/Gyml\/).*(?=\.spl__WeaponInfoSpecial\.gyml)"
    )
    sub_regex = re.compile(r"(?<=Work\/Gyml\/).*(?=\.spl__WeaponInfoSub\.gyml)")
    for weapon in weapon_data:
        weapon["Name"] = localize(language_data, weapon["__RowId"])
        weapon["Class"] = weapon["__RowId"].split("_")[0]
        special = special_regex.search(weapon["SpecialWeapon"]).group(0)
        sub = sub_regex.search(weapon["SubWeapon"]).group(0)
        weapon["Special"] = localize(language_data, special)
        weapon["Sub"] = localize(language_data, sub)

    return weapon_data


def get_versus_weapons_simplified(
    version: str | None = None, lang: str = "USen"
) -> WeaponsMap:
    """Get the versus weapons from the specified version of the datamine, but in
    a simplified and localized format. If no version is specified, get the
    latest version. If no language is specified, use English.

    Args:
        version (str | None): The version to get the data from. If None, get the
            latest version. Defaults to None.
        lang (str): The language to use. Defaults to "USen".

    Returns:
        WeaponsMap: The versus weapons.
    """
    full_list = map_localized_names(
        get_versus_weapons(version=version), lang=lang
    )
    out = {}
    for weapon in full_list:
        dic = {
            k: v
            for k, v in weapon.items()
            if k
            in [
                "Name",
                "Special",
                "Sub",
                "Range",
                "SpecialPoint",
                "Class",
            ]
        }
        out[dic["Name"]] = dic
    return out
