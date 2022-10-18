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
        level2 = level1_loaded["a"]
        level2_sliced = level2[:]
        assert level2["b", 0, "c"] == 3

    def test_getattr_toplevel(self, level0_loaded) -> None:
        assert level0_loaded.test_attribute() == [1]
        with pytest.raises(AttributeError):
            level0_loaded.test_nonexistent_attribute()

    def test_search_by_id(
        self, level0_loaded_with_id, level1_with_id_class
    ) -> None:
        level1 = level0_loaded_with_id.search_by_id("0")
        assert isinstance(level1, level1_with_id_class)
        assert level1.id == 0

        level1 = level0_loaded_with_id.search_by_id(0)
        assert isinstance(level1, level1_with_id_class)
        assert level1.id == 0

    def test_traverse_tree(self, level0_loaded) -> None:
        def stringify(node: Any) -> str:
            return str(node)

        level0_loaded.traverse_tree(stringify)


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
        anarchy_loaded: battleSchema,
        path: tuple,
        expected: Any,
    ) -> None:
        """Test that the schema can get correct attributes from the JSON."""
        true_path = base_path + path
        test_json = json_path(anarchy_full_json, true_path)
        assert anarchy_loaded[true_path] == test_json
        assert anarchy_loaded[true_path] == expected

    def test_rgb(self, anarchy_loaded: battleSchema) -> None:
        path = base_path + ("player", "nameplate", "background", "textColor")
        assert anarchy_loaded[path].to_hex_rgb() == "#ffffff"
        assert (
            anarchy_loaded[path].to_hex_rgb(include_alpha=True) == "#ffffffff"
        )

    def test_calculate_ability(self, anarchy_loaded: battleSchema) -> None:
        path = base_path + ("player",)
        abilities = anarchy_loaded[path].calculate_abilities()
        assert abilities == {
            "Ink Recovery Up": 33,
            "Intensify Action": 6,
            "Ink Saver (Main)": 3,
            "Run Speed Up": 3,
            "Special Saver": 3,
            "Sub Power Up": 3,
            "Swim Speed Up": 3,
        }
