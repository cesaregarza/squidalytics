import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from squidalytics.schemas.base import JSONDataClass

input_path = Path(__file__).parent.parent / "input_files"


@pytest.fixture
def test_json_dict() -> dict:
    test_json_path = str(input_path / "test_json.json")
    with open(test_json_path, "r") as f:
        test_json = json.load(f)
    return test_json[0]


@pytest.fixture
def test_json_list() -> list[dict]:
    test_json_path = str(input_path / "test_json.json")
    with open(test_json_path, "r") as f:
        test_json = json.load(f)
    return test_json


@dataclass(repr=False)
class Level3:
    c: int
    d: None
    e: str


@dataclass(repr=False)
class Level2:
    b: list[Level3]


@dataclass(repr=False)
class Level1(JSONDataClass):
    a: Level2


@dataclass
class Level0(JSONDataClass):
    data: list[Level1]


class AnnotationLevel0(JSONDataClass):
    a: int


class AnnotationLevel1(JSONDataClass):
    b: int


class AnnotationLevel2(JSONDataClass):
    c: int


@pytest.fixture
def level0_class() -> Level0:
    return Level0


@pytest.fixture
def annotation_level0_class() -> AnnotationLevel0:
    return AnnotationLevel0
