import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from squidalytics.schemas.base import JSONDataClass, JSONDataClassListTopLevel

input_path = Path(__file__).parent.parent / "input_files"


@pytest.fixture
def simple_json_path() -> Path:
    return input_path / "test_simple_json.json"


@pytest.fixture
def simple_json_list(simple_json_path: Path) -> list[dict]:
    with open(str(simple_json_path), "r") as f:
        simple_json = json.load(f)
    return simple_json


@dataclass(repr=False)
class SimpleLevel2(JSONDataClass):
    b: int


@dataclass(repr=False)
class SimpleLevel1(JSONDataClass):
    a: SimpleLevel2


class SimpleLevel0(JSONDataClassListTopLevel):
    next_level_type = SimpleLevel1


@pytest.fixture
def simple_level0_class() -> SimpleLevel0:
    return SimpleLevel0


@pytest.fixture
def simple_level0_loaded(simple_json_list) -> SimpleLevel0:
    return SimpleLevel0(simple_json_list)
