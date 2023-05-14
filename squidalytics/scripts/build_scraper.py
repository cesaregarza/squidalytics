import os
from datetime import datetime as dt
from typing import TypeAlias

import numpy as np
import numpy.typing as npt
import pandas as pd
import sqlalchemy as sa
from dotenv import load_dotenv
from sqlalchemy.engine import URL

from squidalytics.analytics.build_consensus.main import generate_all_abilities
from squidalytics.analytics.build_consensus.scrape_sendou import (
    scrape_sendou_builds,
)

load_dotenv()

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
    out["author"] = build["author"].replace("\x00", "")
    out["plus"] = build["plus"]
    out["top_500"] = build["top_500"]
    out["hash"] = build["hash"]
    out["abilities"] = ",".join(build["abilities"])
    return out


def get_existing_hashes(engine: sa.engine.Engine) -> list[str]:
    query = "SELECT hash FROM builds"
    return pd.read_sql(query, engine)["hash"].tolist()


def scrape(engine: sa.engine.Engine) -> None:
    existing_hashes = get_existing_hashes(engine)
    scraped_builds = scrape_sendou_builds(48, hash_list=existing_hashes)
    builds_df = sqlify_scraped_builds(scraped_builds)
    if len(builds_df) == 0:
        return
    builds_df.to_sql("builds", engine, if_exists="append", index=False)


def main() -> None:
    engine_data = {
        "username": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv("POSTGRES_PORT"),
        "database": os.getenv("POSTGRES_DB"),
    }
    url_object = URL.create("postgresql+psycopg2", **engine_data)
    engine = sa.create_engine(url_object)
    scrape(engine)


if __name__ == "__main__":
    main()
