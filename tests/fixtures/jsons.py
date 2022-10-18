import json
from pathlib import Path

import pytest

from squidalytics.schemas.battle import battleSchema

input_path = Path(__file__).parent.parent / "input_files"


def json_path(
    test_json: dict, path: tuple[str | int, ...]
) -> dict | list[dict]:
    """Get a value from a nested dictionary by a path of keys. Replaces having
    to the messy syntax of `test_json["key1"]["key2"]`.

    Args:
        test_json (dict): The dictionary to get the value from.
        path (tuple[str | int, ...]): The path of keys to get the value from.

    Returns:
        dict | list[dict]: The value at the end of the path.
    """
    out: dict | list[dict] = test_json
    for key in path:
        out = out[key]
    return out


@pytest.fixture
def anarchy_full_json() -> dict:
    anarchy_path = str(input_path / "test_anarchy.json")
    with open(anarchy_path, "r") as f:
        anarchy = json.load(f)
    return anarchy


@pytest.fixture
def anarchy_loaded(anarchy_full_json: dict) -> battleSchema:
    return battleSchema(anarchy_full_json)
