from dataclasses import dataclass

from squidalytics.schemas.base import JSONDataClass
from squidalytics.schemas.overview.coop import CoopResultSchema
from squidalytics.schemas.overview.history_groups import (
    anarchyHistoryGroupsSchema,
    regularHistoryGroupsSchema,
)
from squidalytics.schemas.overview.history_groups_only_first import (
    historyGroupsOnlyFirstSchema,
)


@dataclass(repr=False)
class SummarySchema(JSONDataClass):
    assistAverage: float
    deathAverage: float
    killAverage: float
    lose: int
    perUnitTimeMinute: int
    specialAverage: float
    win: int


@dataclass(repr=False)
class anarchyBattleHistorySchema(JSONDataClass):
    historyGroups: anarchyHistoryGroupsSchema
    historyGroupsOnlyFirst: historyGroupsOnlyFirstSchema
    summary: SummarySchema


@dataclass(repr=False)
class regularBattleHistorySchema(JSONDataClass):
    historyGroups: regularHistoryGroupsSchema
    historyGroupsOnlyFirst: historyGroupsOnlyFirstSchema
    summary: SummarySchema
