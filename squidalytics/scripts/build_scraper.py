from datetime import datetime as dt
from typing import TypeAlias

import numpy as np
import numpy.typing as npt
import pandas as pd
import sqlalchemy as sa

from squidalytics.analytics.build_consensus.main import generate_all_abilities
from squidalytics.analytics.build_consensus.scrape_sendou import (
    scrape_sendou_builds,
)

BuildType: TypeAlias = dict[str, str | list[dict[str, str | list[dict]]]]

MODES = ["Turf War", "Splat Zones", "Tower Control", "Rainmaker", "Clam Blitz"]


def sqlify_scraped_builds(builds: list[BuildType]) -> pd.DataFrame:
    out: list[dict] = []
    date = dt.now()
    for category in builds:
        category_name = category["category"]
        for weapon in category["weapons"]:
            weapon_name = weapon["weapon"]
            for build in weapon["builds"]:
                out.append(
                    {
                        "category": category_name,
                        "weapon": weapon_name,
                        "date": date,
                        **sqlify_build(build),
                    }
                )
    return pd.DataFrame(out)


def sqlify_weapon(build: BuildType, category: str) -> dict:
    out = {}
    out["weapon"] = build["weapon"]
    out["category"] = category
    out["builds"] = sqlify_build(build["builds"])
    return out


def sqlify_build(build: dict) -> dict:
    out = {}
    for mode in MODES:
        out[mode] = mode in build["modes"]
    out["author"] = build["author"]
    out["plus"] = build["plus"]
    out["top_500"] = build["top_500"]
    out["hash"] = build["hash"]
    out["abilities"] = ",".join(build["abilities"])
    return out


def get_existing_hashes(conn: sa.engine.Connection) -> list[str]:
    query = sa.select([sa.column("hash")]).select_from(sa.table("builds"))
    return [row["hash"] for row in conn.execute(query)]


def scrape(conn: sa.engine.Connection) -> None:
    existing_hashes = get_existing_hashes(conn)
    scraped_builds = scrape_sendou_builds(1000, hash_list=existing_hashes)
