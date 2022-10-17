from dataclasses import dataclass
from typing import Any

import pytest

from squidalytics.schemas.base import JSONDataClass, SecondaryException
from squidalytics.schemas.battle import (
    awardsSchema,
    backgroundSchema,
    badgeSchema,
    badgesSchema,
    bankaraMatchSchema,
    battleDataSchema,
    battleNodeSchema,
    battleSchema,
    brandSchema,
    gearPowerSchema,
    gearSchema,
    nameplateSchema,
    playerFullSchema,
    playerSchema,
    resultSchema,
    teamSchema,
    usualGearPowerSchema,
    vsHistoryDetailSchema,
)
from tests.fixtures.jsons import json_path

base_path = (0, "data", "vsHistoryDetail")


class TestJsonDataClass:
    def test_init(self, test_json_dict, level1_class) -> None:
        with pytest.raises(TypeError):
            test = JSONDataClass(**test_json_dict)
        test = level1_class(**test_json_dict)
        assert isinstance(test, JSONDataClass)
        json_copy = {**test_json_dict}
        json_copy["blank"] = None
        with pytest.raises(TypeError):
            test = level1_class(**json_copy)
        test_json_dict["a"] = {}
        with pytest.raises(SecondaryException):
            test = level1_class(**test_json_dict)

    def test_init_list(
        self,
        test_json_list,
        level0_class,
        level1_class,
        level0_dataclass,
    ) -> None:
        with pytest.raises(TypeError):
            JSONDataClass(test_json_list)
        with pytest.raises(TypeError):
            heterogeneous_list = test_json_list + [None]
            level0_class(heterogeneous_list)
        test = level0_class(test_json_list)
        assert isinstance(test, JSONDataClass)
        assert len(test.data) == 1
        assert isinstance(test.data[0], level1_class)
        with pytest.raises(TypeError):
            level0_dataclass(test_json_list)

    def test_repr(self, level0_loaded) -> None:
        level0_repr = repr(level0_loaded)
        expected = (
            "Level0:\n"
            + " data: list[Level1]\n"
            + "  a:\n"
            + "   b: list[Level3]\n"
            + "    c: int\n"
            + "    d: NoneType\n"
            + "    e: str\n"
            + "    _g: NoneType\n"
            + "    h: list[]\n"
            + "    i: list[list]\n"
            + "      []\n"
            + "  j: int\n"
        )
        assert level0_repr == expected

    def test_getitem_toplevel(self, level0_loaded, level1_class) -> None:
        with pytest.raises(TypeError):
            level0_loaded["test"]
        level0_sliced = level0_loaded[:]
        assert len(level0_sliced.data) == 1
        with pytest.raises(TypeError):
            level0_loaded["test", 0]
        c_val = level0_loaded[0, "a", "b", 0, "c"]
        assert c_val == 3
        level1 = level0_loaded[0]
        assert isinstance(level1, level1_class)

    def test_getitem(self, level1_loaded) -> None:
        with pytest.raises(IndexError):
            level1_loaded[0]
        with pytest.raises(IndexError):
            level1_loaded[:]

    def test_getattr_toplevel(self, level0_loaded) -> None:
        assert level0_loaded.test_attribute() == [1]
        with pytest.raises(AttributeError):
            level0_loaded.test_nonexistent_attribute()


class TestAnarchySchema:
    @pytest.mark.parametrize(
        "path, expected",
        [
            (("vsRule", "name"), "Clam Blitz"),
            (("vsRule", "rule"), "CLAM"),
            (("vsMode", "mode"), "BANKARA"),
            (("player", "name"), "Joy"),
            (("player", "nameplate", "background", "textColor", "a"), 1.0),
        ],
    )
    def test_getattr(
        self,
        anarchy_full_json: dict,
        anarchy_battle_schema: battleSchema,
        path: tuple,
        expected: Any,
    ) -> None:
        """Test that the schema can get correct attributes from the JSON."""
        true_path = base_path + path
        test_json = json_path(anarchy_full_json, true_path)
        assert anarchy_battle_schema[true_path] == test_json
        assert anarchy_battle_schema[true_path] == expected
