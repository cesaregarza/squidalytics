import hashlib
import json
from typing import cast

import bs4
import numpy as np
import numpy.typing as npt
import requests

from squidalytics.analytics.build_consensus.main import (
    bin_abilities,
    generate_adjacency_matrix,
    generate_consensus_matrix,
)

base_url = "https://sendou.ink/builds"

ability_map_cont = {
    "ISM": "Ink Saver (Main)",
    "ISS": "Ink Saver (Sub)",
    "IRU": "Ink Recovery Up",
    "RSU": "Run Speed Up",
    "SSU": "Swim Speed Up",
    "SCU": "Special Charge Up",
    "SS": "Special Saver",
    "SPU": "Special Power Up",
    "QR": "Quick Respawn",
    "QSJ": "Quick Super Jump",
    "BRU": "Sub Power Up",
    "RES": "Ink Resistance Up",
    "SRU": "Sub Resistance Up",
    "IA": "Intensify Action",
}
ability_map_disc = {
    "OG": "Opening Gambit",
    "LDE": "Last-Ditch Effort",
    "T": "Tenacity",
    "CB": "Comeback",
    "NS": "Ninja Squid",
    "H": "Haunt",
    "TI": "Thermal Ink",
    "RP": "Respawn Punisher",
    "AD": "Ability Doubler",
    "SJ": "Stealth Jump",
    "OS": "Object Shredder",
    "DR": "Drop Roller",
}


def build_weapon_url(weapon: str, limit: int = 48) -> str:
    return f"{base_url}/{weapon}?limit={limit}"


def map_ability(ability: str) -> str:
    pre, _ = ability.split("-")
    if pre in ability_map_disc:
        return ability_map_disc[pre]
    elif pre in ability_map_cont:
        return ability_map_cont[pre]
    else:
        return ability


def get_abilities(build: bs4.element.Tag) -> dict[str, int]:
    abilities: list[bs4.element.Tag] = build.find_all(
        "div", class_="build__ability"
    )
    out = {}
    for i, ability in enumerate(abilities):
        ability_name = ability["data-testid"]
        weight = 10 if i % 4 == 0 else 3
        mapped_name = map_ability(ability_name)
        if mapped_name in out:
            out[mapped_name] += weight
        else:
            out[mapped_name] = weight
    return out


def get_misc_data(build: bs4.element.Tag) -> dict:
    misc_data: dict = {}
    # Modes
    modes_raw = build.select("div.build__modes picture")
    modes = [mode["title"] for mode in modes_raw]
    misc_data["modes"] = modes

    # Author and plus status
    author_row = build.select_one("div.build__date-author-row")
    author = author_row.select_one("a").text
    try:
        plus = int(author_row.select_one("span").text[1])
    except AttributeError:
        plus = 0
    misc_data["author"] = author
    misc_data["plus"] = plus

    # Top 500 status
    top_500_path = (
        "div.build__weapons div.build__weapon picture img.build__top500"
    )
    top_500 = build.select_one(top_500_path) is not None
    misc_data["top_500"] = top_500
    return misc_data


def get_build_data(build: bs4.element.Tag) -> dict:
    abilities = get_abilities(build)
    misc_data = get_misc_data(build)
    out = {**misc_data, "abilities": abilities}
    hash = hashlib.sha256(json.dumps(out).encode("utf-8")).hexdigest()
    out["hash"] = hash
    return out


def get_builds_data(
    builds: list[bs4.element.Tag], hash_list: list[str] | None = None
) -> list[dict]:
    builds_data = []
    for build in builds:
        build_data = get_build_data(build)
        if (hash_list is not None) and (build_data["hash"] in hash_list):
            break
        builds_data.append(build_data)
    return builds_data


def bin_builds(builds: list[dict], bin_size: int = 10) -> list[dict]:
    return [
        {
            k: v if k != "abilities" else bin_abilities(v, bin_size)
            for k, v in build.items()
        }
        for build in builds
    ]


def get_all_abilities(builds: list[dict]) -> list[str]:
    abilities = set()
    for build in builds:
        for ability in build["abilities"]:
            abilities.add(ability)

    abilities_list = list(abilities)
    abilities_list.sort()
    return abilities_list


def assign_adjacency_matrix(
    builds: list[dict], all_abilities: list[str]
) -> list[dict]:
    for build in builds:
        abilities_list = list(build["abilities"])
        build["adjacency_tensor"] = generate_adjacency_matrix(
            abilities_list, all_abilities
        )
    return builds


def scrape_weapon_builds(
    weapon: str,
    limit: int,
    bin_size: int = 10,
    hash_list: list[str] | None = None,
) -> list[dict]:
    page = requests.get(build_weapon_url(weapon, limit))
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    builds = soup.find_all("div", class_="build")
    builds_data = get_builds_data(builds, hash_list)
    builds_data = bin_builds(builds_data, bin_size)
    all_abilities = get_all_abilities(builds_data)
    builds_data = assign_adjacency_matrix(builds_data, all_abilities)
    return builds_data


def scrape_sendou_builds(
    limit: int, bin_size: int = 10, hash_list: list[str] | None = None
) -> list[dict[list[dict]]]:
    base_page = requests.get(base_url)
    soup = bs4.BeautifulSoup(base_page.content, "html.parser")
    categories = soup.find_all("div", class_="builds__category")
    out: list[dict[list[dict]]] = []
    for category in categories:
        category = cast(bs4.element.Tag, category)
        sub_out = {}
        sub_out["category"] = category.find(
            "div", class_="builds__category__header"
        ).text
        weapons = category.find_all("a", class_="builds__category__weapon")
        weapons_list: list[dict[list[dict]]] = []

        for weapon in weapons:
            weapon = cast(bs4.element.Tag, weapon)
            weapon_name = weapon.attrs["href"].split("/")[-1]
            weapon_data = scrape_weapon_builds(
                weapon_name, limit, bin_size, hash_list
            )
            weapons_list.append({
                "weapon": weapon_name,
                "builds": weapon_data,
            })
        sub_out["weapons"] = weapons_list
        out.append(sub_out)
    return out


def restrict_player_influence(builds: list[dict]) -> npt.NDArray[np.float64]:
    # Count the number of builds submitted by each player.
    counter = {}
    for build in builds:
        author = build["author"]
        counter[author] = counter.get(author, 0) + 1

    # Calculate the weight for each build.
    weights = []
    for build in builds:
        author = build["author"]
        weights.append(1 / counter[author])

    return np.array(weights)


def plus_influence(
    builds: list[dict],
    base_multiplier: float = 1.0,
    plus_multiplier: float = 1.2,
) -> npt.NDArray[np.float64]:
    weights = []
    for build in builds:
        plus = build["plus"]
        value = (
            base_multiplier * plus_multiplier ** (4 - plus) if plus > 0 else 1
        )
        weights.append(value)
    return np.array(weights)


def modes_filter(
    builds: list[dict], modes: list[str], invert: bool = False
) -> npt.NDArray[np.float64]:
    weights = []
    value_if_true = 1 if not invert else 0
    value_if_false = 0 if not invert else 1
    for build in builds:
        build_modes = build["modes"]
        if any(mode in build_modes for mode in modes):
            weights.append(value_if_true)
        else:
            weights.append(value_if_false)
    return np.array(weights)
