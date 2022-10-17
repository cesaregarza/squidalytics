from typing import Any

import pytest

from squidalytics.schemas.base import JSONDataClass
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
    def test_init(self, test_json_dict: dict) -> None:
        test = JSONDataClass(**test_json_dict)


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
