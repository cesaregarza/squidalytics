import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from squidalytics.schemas.base import JSONDataClass, JSONDataClassListTopLevel

input_path = Path(__file__).parent.parent / "input_files"


@pytest.fixture
def test_json_path() -> Path:
    return input_path / "test_json.json"


@pytest.fixture
def test_json_dict(test_json_path: Path) -> dict:
    with open(str(test_json_path), "r") as f:
        test_json = json.load(f)
    return test_json[0]


@pytest.fixture
def test_json_list(test_json_path: Path) -> list[dict]:
    with open(str(test_json_path), "r") as f:
        test_json = json.load(f)
    return test_json


@pytest.fixture
def test_json_list_with_id() -> list[dict]:
    test_json_path = str(input_path / "test_json_with_id.json")
    with open(test_json_path, "r") as f:
        test_json = json.load(f)
    return test_json


@dataclass(repr=False)
class Level3(JSONDataClass):
    c: int
    d: None
    e: str
    _g: None
    h: list
    i: list = None


@dataclass(repr=False)
class Level2(JSONDataClass):
    b: list[Level3]


@dataclass(repr=False)
class Level1(JSONDataClass):
    a: Level2
    j: int = 1

    def test_attribute(self) -> int:
        return 1


class Level0(JSONDataClassListTopLevel):
    next_level_type = Level1


@dataclass(repr=False)
class Level0DataClass(JSONDataClassListTopLevel):
    data: list[Level1]


@dataclass(repr=False)
class Level3WithID(JSONDataClass):
    c: int
    d: None
    e: str
    _g: None
    h: list
    i: list = None
    id: int = None


@dataclass(repr=False)
class Level2WithID(JSONDataClass):
    b: list[Level3WithID]
    id: int = None


@dataclass(repr=False)
class Level1WithID(JSONDataClass):
    a: Level2WithID
    j: int = 1
    id: int = None


class Level0WithID(JSONDataClassListTopLevel):
    next_level_type = Level1WithID


@pytest.fixture
def level0_class() -> Level0:
    return Level0


@pytest.fixture
def level0_dataclass() -> Level0DataClass:
    return Level0DataClass


@pytest.fixture
def level1_class() -> Level1:
    return Level1


@pytest.fixture
def level1_with_id_class() -> Level1WithID:
    return Level1WithID


@pytest.fixture
def level0_loaded(test_json_list) -> Level0:
    return Level0(test_json_list)


@pytest.fixture
def level1_loaded(test_json_dict) -> Level1:
    return Level1(**test_json_dict)


@pytest.fixture
def level0_loaded_with_id(test_json_list_with_id) -> Level0:
    return Level0WithID(test_json_list_with_id)
