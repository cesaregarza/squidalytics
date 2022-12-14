from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from squidalytics.analytics.plots.heatmap import heatmap
from squidalytics.constants import ABILITIES, ALL_ABILITIES, WEAPON_MAP
from squidalytics.data.scrape_version_releases import map_date_to_version
from squidalytics.schemas.base import JSONDataClass, JSONDataClassListTopLevel
from squidalytics.schemas.general import (
    colorSchema,
    idSchema,
    imageSchema,
    vsModeSchema,
    vsRuleSchema,
    vsStageSchema,
    weaponSchema,
)
from squidalytics.utils import aggregate_masking


@dataclass(repr=False)
class badgeSchema(JSONDataClass):
    id: str = None
    image: imageSchema = None


@dataclass(repr=False)
class badgesSchema(JSONDataClass):
    badges: list[badgeSchema]


@dataclass(repr=False)
class backgroundSchema(JSONDataClass):
    textColor: colorSchema
    image: imageSchema
    id: str


@dataclass(repr=False)
class nameplateSchema(JSONDataClass):
    badges: badgesSchema
    background: backgroundSchema


@dataclass(repr=False)
class gearPowerSchema(JSONDataClass):
    name: str
    image: imageSchema


@dataclass(repr=False)
class usualGearPowerSchema(JSONDataClass):
    name: str
    desc: str
    image: imageSchema
    isEmptySlot: bool


@dataclass(repr=False)
class brandSchema(JSONDataClass):
    name: str
    image: imageSchema
    id: str
    usualGearPower: usualGearPowerSchema


@dataclass(repr=False)
class gearSchema(JSONDataClass):
    name: str
    _isGear: str
    primaryGearPower: gearPowerSchema
    additionalGearPowers: list[gearPowerSchema]
    originalImage: imageSchema
    brand: brandSchema
    image: imageSchema = None
    thumbnailImage: imageSchema = None

    def calculate_abilities(self) -> dict[str, int]:
        """Calculate the total ability points for each ability, even primary
        only abilities.

        Returns:
            dict[str, int]: A dictionary of ability names and their total
        """
        abilities = {ability: 0 for ability in ALL_ABILITIES}
        primary_ability = self.primaryGearPower.name
        abilities[primary_ability] += 10
        for ability in self.additionalGearPowers:
            if ability.name.lower() == "unknown":
                continue
            abilities[ability.name] += 3
        return abilities

    def classify_gear(self) -> str:
        """Classify the gear based on the abilities it has.

        Returns:
            str: The gear classification, one of "perfect", "complete",
            "incomplete", or "mixed".
        """
        abilities = self.calculate_abilities()
        # Primary adds 10, secondary adds 3. 19 points is thus perfect gear.
        if any(abilities[ability] == 19 for ability in ABILITIES):
            return "perfect"

        # If the sum of all abilities is less than 19, it hasn't unlocked
        # all of the sub-abilities.
        if sum(abilities[ability] for ability in ABILITIES) < 19:
            return "incomplete"

        # The only way to get 9 points is to have 3 of the same sub-ability.
        if any(abilities[ability] == 9 for ability in ABILITIES):
            return "complete"

        # Otherwise, it's a mixed gear.
        return "mixed"


@dataclass(repr=False)
class resultSchema(JSONDataClass):
    kill: int = None
    death: int = None
    assist: int = None
    special: int = None
    noroshiTry: None = None
    paintRatio: float = None
    score: int = None
    noroshi: None = None


@dataclass(repr=False)
class playerSchema(JSONDataClass):
    _isPlayer: str
    byname: str
    name: str
    nameId: str
    nameplate: nameplateSchema
    id: str
    headGear: gearSchema
    clothingGear: gearSchema
    shoesGear: gearSchema
    paint: int

    @property
    def full_name(self) -> str:
        return self.name + "#" + self.nameId

    def calculate_abilities(self) -> dict[str, int]:
        """Calculate the total ability points for all gear.

        Returns:
            dict[str, int]: A dictionary of ability names and their total,
                sorted by total points and dropping abilities with 0 points.
        """
        abilities = {ability: 0 for ability in ALL_ABILITIES}
        for gear in [self.headGear, self.clothingGear, self.shoesGear]:
            gear_abilities = gear.calculate_abilities()
            for ability, value in gear_abilities.items():
                abilities[ability] += value
        # Sort the abilities by their value, then by their name, and remove
        # keys with a value of 0.
        abilities = {
            ability: value
            for ability, value in sorted(
                abilities.items(),
                key=lambda item: (item[1], item[0]),
                reverse=True,
            )
            if value > 0
        }
        return abilities


@dataclass(repr=False)
class playerFullSchema(playerSchema):
    isMyself: bool
    species: str
    festDragonCert: str
    _typename: str
    weapon: weaponSchema
    result: resultSchema = None

    def summary(self, version: str | None = None) -> dict:
        """Return a summary of the player's battle stats.

        Args:
            version (str | None, optional): The version of the game to use for
                the weapon details. Defaults to None.

        Returns:
            dict: A dictionary of the player's stats.
        """
        out = {
            "name": self.full_name,
            "abilities": self.calculate_abilities(),
            "weapon": self.weapon.name,
            "weapon_id": self.weapon.id,
            "species": self.species,
            "paint": self.paint,
        }
        out["weapon_details"] = self.weapon_details(version=version)
        if self.result:
            append = {
                "elimination": self.result.kill,
                "kill": self.result.kill - self.result.assist,
                "death": self.result.death,
                "special": self.result.special,
                "assist": self.result.assist,
            }
        else:
            append = {
                "elimination": 0,
                "kill": 0,
                "death": 0,
                "special": 0,
                "assist": 0,
            }
        out.update(append)
        return out

    def weapon_details(self, version: str | None = None) -> dict:
        if version is None:
            return WEAPON_MAP.versus_weapons[self.weapon.name]
        return WEAPON_MAP[version].versus_weapons[self.weapon.name]


@dataclass(repr=False)
class teamSchema(JSONDataClass):
    color: colorSchema
    judgement: str
    players: list[playerFullSchema]
    order: int
    result: resultSchema = None
    tricolorRole: str = None
    festTeamName: str = None

    @property
    def is_my_team(self) -> bool:
        """Check if the team is the team the user is on.

        Returns:
            bool: True if the team is the user's team, False otherwise.
        """
        return any(player.isMyself for player in self.players)

    @property
    def score(self) -> int | float:
        """Get the team's score.

        Returns:
            int: The team's score.
        """
        if self.result and self.result.score:
            return self.result.score
        elif self.result and self.result.paintRatio:
            return self.result.paintRatio * 100
        else:
            return 0

    def player_summary(
        self, detailed: bool = False, version: str | None = None
    ) -> list[dict[str, Any]]:
        """Get a summary of the team's players.

        Args:
            detailed (bool): Whether to include detailed information about the
                player. Defaults to False.
            version (str | None, optional): The version of the game to use for
                the weapon details. Defaults to None.

        Returns:
            list[dict]: A list of dictionaries containing the player's stats.
        """
        out: list[dict[str, Any]] = []
        for player in self.players:
            out.append(player.summary(version=version))
        if not detailed:
            return out
        # Add additional information if detailed is True.
        team_stats = self.team_summary(player_summaries=out)
        for player_dict in out:

            def ratio(key: str) -> float:
                return player_dict[key] / max(team_stats[key], 1)

            player_dict["kill_ratio"] = ratio("kill")
            player_dict["death_ratio"] = ratio("death")
            player_dict["special_ratio"] = ratio("special")
            player_dict["assist_ratio"] = ratio("assist")
            player_dict["paint_ratio"] = ratio("paint")
            player_dict["kdr"] = player_dict["kill"] / max(
                player_dict["death"], 1
            )
        return out

    def team_summary(
        self,
        player_summaries: list[dict] | None = None,
        detailed: bool = False,
        version: str | None = None,
    ) -> dict:
        """Get an overall summary of the team.

        Args:
            player_summaries (list[dict], optional): A list of player summaries
                to use. If None, the player summaries will be calculated.
                Passing in a list of player summaries reduces redundant work.
                Defaults to None.
            detailed (bool): Whether to include detailed information about the
                team. Defaults to False.
            version (str | None, optional): The version of the game to use for
                the weapon details. Defaults to None.

        Returns:
            dict: A dictionary of team statistics.
        """
        if player_summaries is None:
            player_summaries = [
                player.summary(version=version) for player in self.players
            ]
        team_total = {
            "kill": sum(player["kill"] for player in player_summaries),
            "death": sum(player["death"] for player in player_summaries),
            "special": sum(player["special"] for player in player_summaries),
            "assist": sum(player["assist"] for player in player_summaries),
            "paint": sum(player["paint"] for player in player_summaries),
            "score": self.score,
        }
        if not detailed:
            return team_total

        # Add additional information if detailed is True.
        weapon_ranges = [
            player["weapon_details"]["Range"] for player in player_summaries
        ]
        team_total["range_mean"] = np.mean(weapon_ranges)
        team_total["range_var"] = np.var(weapon_ranges)
        team_total["range_median"] = np.median(weapon_ranges)
        return team_total


@dataclass(repr=False)
class bankaraMatchSchema(JSONDataClass):
    mode: str
    earnedUdemaePoint: int = None


@dataclass(repr=False)
class awardsSchema(JSONDataClass):
    name: str
    rank: str


@dataclass(repr=False)
class vsHistoryDetailSchema(JSONDataClass):
    _typename: str
    id: str
    vsRule: vsRuleSchema
    vsMode: vsModeSchema
    player: playerSchema
    judgement: str
    myTeam: teamSchema
    vsStage: vsStageSchema
    otherTeams: list[teamSchema]
    awards: list[awardsSchema]
    duration: int
    playedTime: str
    festMatch: str = None
    knockout: str = None
    bankaraMatch: bankaraMatchSchema = None
    xMatch: str = None
    leagueMatch: str = None
    nextHistoryDetail: idSchema = None
    previousHistoryDetail: idSchema = None

    def count_awards(self) -> list[tuple[str, str]]:
        """Count the number of times each award was received.

        Returns:
            list:
                tuple:
                    str: The name of the award.
                    str: The rank of the award.
        """
        return [(award.name, award.rank) for award in self.awards]

    def my_stats(self, detailed: bool = False) -> dict:
        """Get the stats for the user's team.

        Args:
            detailed (bool): Whether to include detailed information about the
                player. Defaults to False.

        Raises:
            ValueError: If the user's stats is not found.

        Returns:
            dict: A dictionary of the user's team's stats.
        """
        players_summary = self.myTeam.player_summary(
            detailed=detailed, version=self.version
        )
        for player in players_summary:
            if player["name"] == self.player.full_name:
                return player
        raise ValueError("Could not find user's stats.")

    def summary(self, detailed: bool = False) -> dict:
        """Get a summary of the match.

        Args:
            detailed (bool): Whether to include detailed information about the
                match. Defaults to False.

        Returns:
            dict: A dictionary of the match's stats.
        """
        out = {
            "me": self.player.full_name,
            "rule": self.vsRule.name,
            "mode": self.vsMode.mode,
            "stage": self.vsStage.name,
            "judgement": self.judgement,
            "knockout": self.knockout,
            "duration": self.duration,
            "played_time": self.playedTime,
            "version": self.version,
            "my_stats": self.my_stats(),
            "my_team": self.myTeam.player_summary(
                detailed=True, version=self.version
            ),
            "other_teams": [
                team.player_summary(detailed=True, version=self.version)
                for team in self.otherTeams
            ],
            "awards": self.count_awards(),
            "my_team_stats": self.myTeam.team_summary(
                detailed=detailed, version=self.version
            ),
            "other_team_stats": [
                team.team_summary(detailed=detailed, version=self.version)
                for team in self.otherTeams
            ],
        }
        return out

    @cached_property
    def version(self) -> str:
        return map_date_to_version(self.played_time_dt)

    @cached_property
    def played_time_dt(self) -> datetime:
        """Get the time the match was played as a datetime object.

        Returns:
            datetime: The time the match was played.
        """
        return datetime.strptime(self.playedTime, "%Y-%m-%dT%H:%M:%SZ")


@dataclass(repr=False)
class battleDataSchema(JSONDataClass):
    vsHistoryDetail: vsHistoryDetailSchema


@dataclass(repr=False)
class battleNodeSchema(JSONDataClass):
    data: battleDataSchema

    def match_completed(self) -> bool:
        """Check if the match is completed.

        Returns:
            bool: True if the match is completed, False otherwise.
        """
        return self.data.vsHistoryDetail.judgement != "EXEMPTED_LOSE"

    def match_summary(
        self, detailed: bool = False
    ) -> dict[str, int | float | str | None]:
        """Get a flat summary of the match, with no nested dictionaries.

        Args:
            detailed (bool): Whether to include detailed information
                about the match. Defaults to False.

        Raises:
            ValueError: If the match is a tricolor match.

        Returns:
            dict: A dictionary of the match's stats. No value is a dictionary.
        """
        if len(self.data.vsHistoryDetail.otherTeams) > 1:
            raise ValueError("Flat summary does not support tricolor matches.")
        summary = self.data.vsHistoryDetail.summary(detailed=detailed)
        summary.pop("my_team")
        summary.pop("other_teams")
        my_stats = summary.pop("my_stats")
        my_team_stats = summary.pop("my_team_stats")
        other_team_stats = summary.pop("other_team_stats")[0]

        # Flatten dictionaries
        my_stats_keys = [
            "weapon",
            "paint",
            "elimination",
            "kill",
            "death",
            "special",
            "assist",
        ]
        summary.update({k: my_stats[k] for k in my_stats_keys})
        summary.update(
            {f"my_team_{k}s": my_team_stats[k] for k in my_team_stats}
        )
        summary.update(
            {f"other_team_{k}s": other_team_stats[k] for k in other_team_stats}
        )
        # Flatten Awards
        awards = summary.pop("awards")
        for i, award in enumerate(awards):
            summary[f"award_{i + 1}"] = award[0]
            summary[f"award_{i + 1}_rank"] = award[1]

        return summary


class battleSchema(JSONDataClassListTopLevel):
    next_level_type = battleNodeSchema

    def to_pandas(self, detailed: bool = False) -> pd.DataFrame:
        """Convert the battleSchema to a pandas DataFrame.

        Args:
            detailed (bool): Whether to include detailed information about the
                match in the DataFrame. Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame of the match's stats.
        """
        df = pd.DataFrame(self.match_summary(detailed=detailed))
        df["played_time"] = pd.to_datetime(df["played_time"])
        df["duration"] = pd.to_timedelta(df["duration"], "s")
        df["end_time"] = df["played_time"] + df["duration"]
        return df

    @staticmethod
    def filter_weapons(
        df: pd.DataFrame, weapons: list[str] | str, include: bool = True
    ) -> tuple[pd.DataFrame, list[str], list[str]]:
        """Filter the DataFrame by the given weapons.

        Args:
            df (pd.DataFrame): The DataFrame to filter.
            weapons (list[str] | str): The weapons or classes to filter by.
            include (bool): Whether to include or exclude the given weapons.
                Defaults to True.

        Returns:
            tuple
                pd.DataFrame: The filtered DataFrame.
                list[str]: The weapons that were filtered out.
                list[str]: The weapon classes that were filtered out.
        """
        weapons_list, classes_list = WEAPON_MAP.parse_input(weapons)
        mask = df["weapon"].str.lower().isin(weapons_list)
        mask = mask if include else ~mask
        df = df.loc[mask]
        return df, weapons_list, classes_list

    def winrate_heatmap(
        self,
        groupby_columns: list[str] | str = ["stage", "rule"],
        filter_weapons: list[str] | str | None = None,
        mask_series: list[pd.Series] | pd.Series | None = None,
        mask_operation: str = "and",
        figure_title_suffix: str | None = None,
        fillna_value: int | float | None = None,
        static: bool = False,
    ) -> go.Figure:
        """Create a heatmap of the winrate with the given parameters

        Args:
            groupby_columns (list[str] | str | None): Columns by which to group
                the data by. Defaults to ["stage", "rule"].
            filter_weapons (list[str] | str | None): Weapons to filter the data
                by. If None, no filtering is done. Defaults to None.
            mask_series (list[pd.Series] | pd.Series | None): Pandas Series to
                apply on the given data before grouping. If a list of masks is
            mask_operation (str): The operation to apply on the masks. Only
                supports "and" and "or" operations. Defaults to "and".
            figure_title_suffix (str | None): A suffix to add to the figure
                title. Defaults to None.
            fillna_value (int | float | np.nan | None): The value to fill
                missing groupby combinations with. Defaults to None.
            static (bool): Whether to return a static figure. Defaults to False.

        Returns:
            go.Figure: The resulting figure
        """
        df = self.to_pandas()
        if filter_weapons is not None:
            df, weapons_list, classes_list = self.filter_weapons(
                df, filter_weapons
            )

            if figure_title_suffix is None:
                figure_title_suffix = self.__figure_title_suffix(
                    weapons_list, classes_list
                )

        if isinstance(mask_series, list):
            mask_series = aggregate_masking(
                *mask_series, operation=mask_operation
            )

        if mask_series is not None:
            df = df.loc[mask_series]

        if isinstance(fillna_value, int):
            fillna_value = float(fillna_value)
        elif fillna_value is None:
            fillna_value = np.nan

        winrate, wincount = df.squidalytics.winrate_grid(groupby_columns)
        # Generate kwargs and use defaults if "None" is provided
        kwarg_list = {}
        if fillna_value is not None:
            kwarg_list["fillna_value"] = fillna_value
        if figure_title_suffix is not None:
            kwarg_list["title_suffix"] = figure_title_suffix
        fig = heatmap(
            winrate.unstack(),
            wincount.unstack(),
            **kwarg_list,
        )
        if not static:
            return fig

        return fig.show(renderer="png")

    def __figure_title_suffix(
        self, weapons: list[str], classes: list[str]
    ) -> str | None:
        """Generate a figure title suffix for the given weapons.

        Args:
            weapons (list[str]): The weapons to generate a suffix for.
            classes (list[str]): The classes to generate a suffix for.

        Returns:
            str | None: The figure title suffix. None if no input is given.
        """
        weapons = [x.capitalize() for x in weapons]
        classes = [x.capitalize() for x in classes]
        if len(classes) > 0 and len(classes) < 3:
            return f"{', '.join(classes)}"
        elif len(classes) > 0 and len(classes) >= 3:
            return f"{len(classes)} classes"
        elif len(weapons) > 0 and len(weapons) < 3:
            return f"{', '.join(weapons)}"
        elif len(weapons) > 0 and len(weapons) >= 3:
            return f"{len(weapons)} weapons"
        else:
            return None
