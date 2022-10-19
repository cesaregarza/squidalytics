from dataclasses import dataclass
from typing import Any

import pandas as pd
import pytest

from squidalytics.constants import ALL_ABILITIES
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

    def test_to_dict(self, level1_loaded) -> None:
        level1_dict = level1_loaded.to_dict(False)
        expected_1 = {
            "a": {
                "b": [
                    {
                        "c": 3,
                        "d": None,
                        "e": "f",
                        "__g": None,
                        "h": [],
                        "i": [[], []],
                    },
                    {
                        "c": 4,
                        "d": None,
                        "e": "f",
                        "__g": None,
                        "h": [],
                        "i": [[], []],
                    },
                    {
                        "c": 5,
                        "d": None,
                        "e": "f",
                        "__g": None,
                        "h": [],
                        "i": None,
                    },
                ]
            },
            "j": 1,
        }
        assert level1_dict == expected_1

        expected_2 = {
            "a": {
                "b": [
                    {
                        "c": 3,
                        "e": "f",
                        "h": [],
                        "i": [[], []],
                    },
                    {
                        "c": 4,
                        "e": "f",
                        "h": [],
                        "i": [[], []],
                    },
                    {
                        "c": 5,
                        "e": "f",
                        "h": [],
                    },
                ]
            },
            "j": 1,
        }
        level1_dict = level1_loaded.to_dict(True)
        assert level1_dict == expected_2


class TestAnarchySchema:

    joy_abilities = {
        "Ink Recovery Up": 33,
        "Intensify Action": 6,
        "Ink Saver (Main)": 3,
        "Run Speed Up": 3,
        "Special Saver": 3,
        "Sub Power Up": 3,
        "Swim Speed Up": 3,
    }
    joy_full_name = "Joy#1584"
    joy_summary = {
        "name": joy_full_name,
        "abilities": joy_abilities,
        "weapon": "Splatterscope",
        "weapon_id": "V2VhcG9uLTIwMjA=",
        "species": "INKLING",
        "paint": 1073,
        "elimination": 8,
        "kill": 6,
        "death": 5,
        "special": 4,
        "assist": 2,
    }
    team_stats = {
        "kill": (10 + 10 + 7 + 6),
        "death": (9 + 10 + 11 + 5),
        "assist": (6 + 4 + 1 + 2),
        "special": (2 + 2 + 2 + 4),
        "paint": (970 + 994 + 1327 + 1073),
        "score": 53,
    }
    joy_awards = [
        ("#1 Super Jump Spot", "GOLD"),
        ("#1 Ink Consumer", "SILVER"),
        ("#1 Ink Vac User", "SILVER"),
    ]
    flat_match_summary = {
        "me": "Joy#1584",
        "rule": "Clam Blitz",
        "mode": "BANKARA",
        "stage": "Inkblot Art Academy",
        "judgement": "WIN",
        "knockout": "NEITHER",
        "duration": 300,
        "played_time": "2022-10-04T06:30:14Z",
        "weapon": "Splatterscope",
        "paint": 1073,
        "elimination": 8,
        "kill": 6,
        "death": 5,
        "special": 4,
        "assist": 2,
        "my_team_kills": 33,
        "my_team_deaths": 35,
        "my_team_specials": 10,
        "my_team_assists": 13,
        "my_team_paints": 4364,
        "my_team_scores": 53,
        "other_team_kills": 35,
        "other_team_deaths": 33,
        "other_team_specials": 13,
        "other_team_assists": 12,
        "other_team_paints": 4217,
        "other_team_scores": 51,
        "award_1": "#1 Super Jump Spot",
        "award_1_rank": "GOLD",
        "award_2": "#1 Ink Consumer",
        "award_2_rank": "SILVER",
        "award_3": "#1 Ink Vac User",
        "award_3_rank": "SILVER",
    }

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

    def test_calculate_ability_solo(self, anarchy_loaded: battleSchema) -> None:
        path = base_path + ("player", "headGear")
        abilities = anarchy_loaded[path].calculate_abilities()
        expected_abilities = {k: 0 for k in ALL_ABILITIES}
        expected_abilities["Ink Recovery Up"] = 10
        expected_abilities["Ink Saver (Main)"] = 3
        expected_abilities["Run Speed Up"] = 3
        expected_abilities["Special Saver"] = 3
        assert abilities == expected_abilities

    def test_calculate_ability_all(self, anarchy_loaded: battleSchema) -> None:
        path = base_path + ("player",)
        abilities = anarchy_loaded[path].calculate_abilities()
        assert abilities == self.joy_abilities

    def test_classify_gear(self, anarchy_loaded: battleSchema) -> None:
        complete_path = base_path + ("myTeam", "players", 1, "headGear")
        incomplete_path = base_path + ("myTeam", "players", 0, "clothingGear")
        mixed_path = base_path + ("myTeam", "players", 0, "headGear")
        perfect_path = base_path + ("otherTeams", 0, "players", 2, "headGear")
        assert anarchy_loaded[complete_path].classify_gear() == "complete"
        assert anarchy_loaded[incomplete_path].classify_gear() == "incomplete"
        assert anarchy_loaded[mixed_path].classify_gear() == "mixed"
        assert anarchy_loaded[perfect_path].classify_gear() == "perfect"

    def test_full_name(self, anarchy_loaded: battleSchema) -> None:
        path = base_path + ("player",)
        assert anarchy_loaded[path].full_name == self.joy_full_name

    def test_team_schema(self, anarchy_loaded: battleSchema) -> None:
        path = base_path + ("myTeam",)
        assert anarchy_loaded[path].is_my_team
        assert anarchy_loaded[path].score == 53

    def test_player_schema(self, anarchy_loaded: battleSchema) -> None:
        path = base_path + ("myTeam", "players", 3)
        assert anarchy_loaded[path].summary() == self.joy_summary

    def test_team_player_summary_detailed(
        self, anarchy_loaded: battleSchema
    ) -> None:
        path = base_path + ("myTeam",)
        player_summaries = anarchy_loaded[path].player_summary(True)
        assert len(player_summaries) == 4
        # Use team stats to calculate additional stats in joy_summary
        joy_summary = self.joy_summary.copy()
        team_stats = self.team_stats.copy()
        joy_summary["kill_ratio"] = joy_summary["kill"] / team_stats["kill"]
        joy_summary["death_ratio"] = joy_summary["death"] / team_stats["death"]
        joy_summary["special_ratio"] = (
            joy_summary["special"] / team_stats["special"]
        )
        joy_summary["assist_ratio"] = (
            joy_summary["assist"] / team_stats["assist"]
        )
        joy_summary["paint_ratio"] = joy_summary["paint"] / team_stats["paint"]
        joy_summary["kdr"] = joy_summary["kill"] / joy_summary["death"]
        assert player_summaries[3] == joy_summary

    def test_team_player_summary(self, anarchy_loaded: battleSchema) -> None:
        path = base_path + ("myTeam",)
        player_summaries = anarchy_loaded[path].player_summary(False)
        assert len(player_summaries) == 4
        assert player_summaries[3] == self.joy_summary

    def test_team_summary(self, anarchy_loaded: battleSchema) -> None:
        path = base_path + ("myTeam",)
        team_summary = anarchy_loaded[path].team_summary()
        assert team_summary == self.team_stats

    def test_count_awards(self, anarchy_loaded: battleSchema) -> None:
        path = base_path
        awards = anarchy_loaded[path].count_awards()
        assert awards == self.joy_awards

    def test_my_stats(self, anarchy_loaded: battleSchema) -> None:
        path = base_path
        stats = anarchy_loaded[path].my_stats()
        assert stats == self.joy_summary

    def test_summary(self, anarchy_loaded: battleSchema) -> None:
        path = base_path
        summary = anarchy_loaded[path].summary()
        keyset = [
            "me",
            "rule",
            "mode",
            "stage",
            "judgement",
            "knockout",
            "duration",
            "played_time",
            "my_stats",
            "my_team",
            "other_teams",
            "awards",
            "my_team_stats",
            "other_team_stats",
        ]
        for key in keyset:
            assert key in summary
        assert summary["me"] == "Joy#1584"
        assert summary["rule"] == "Clam Blitz"
        assert summary["mode"] == "BANKARA"
        assert summary["stage"] == "Inkblot Art Academy"
        assert summary["judgement"] == "WIN"
        assert summary["knockout"] == "NEITHER"

    def test_match_completed(self, anarchy_loaded: battleSchema) -> None:
        assert anarchy_loaded[0].match_completed()

    def test_match_summary(self, anarchy_loaded: battleSchema) -> None:
        path = 0
        summary = anarchy_loaded[path].match_summary()

        assert summary == self.flat_match_summary

    def test_to_pandas(self, anarchy_loaded: battleSchema) -> None:
        df = anarchy_loaded.to_pandas()
        assert df.shape == (1, 34)
        assert isinstance(df.loc[0, "played_time"], pd.Timestamp)
        assert isinstance(df.loc[0, "duration"], pd.Timedelta)
        assert isinstance(df.loc[0, "end_time"], pd.Timestamp)
        assert df.loc[0, "played_time"] < df.loc[0, "end_time"]
