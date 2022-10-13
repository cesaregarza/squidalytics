from dataclasses import dataclass

from squidalytics.schemas.base import JSONDataClass
from squidalytics.schemas.overview.history_groups import (
    nextHistoryDetailSchema,
    previousHistoryDetailSchema,
    weaponImageSchema,
)
from squidalytics.schemas.overview.history_groups_only_first import (
    historyGroupsOnlyFirstSchema,
)


@dataclass(repr=False)
class RegularGradeSchema(JSONDataClass):
    name: str
    id: str


@dataclass(repr=False)
class monthlyGearSchema(JSONDataClass):
    _typename: str
    name: str
    image: weaponImageSchema


@dataclass(repr=False)
class scaleSchema(JSONDataClass):
    gold: int
    silver: int
    bronze: int


@dataclass(repr=False)
class pointCardSchema(JSONDataClass):
    defeatBossCount: int
    deliverCount: int
    goldenDeliverCount: int
    playCount: int
    rescueCount: int
    regularPoint: int
    totalPoint: int


@dataclass(repr=False)
class gradeSchema(JSONDataClass):
    name: str
    id: str


@dataclass(repr=False)
class highestResultSchema(JSONDataClass):
    grade: gradeSchema
    gradePoint: int
    jobScore: int


@dataclass(repr=False)
class weaponsNodeSchema(JSONDataClass):
    name: str
    image: weaponImageSchema


@dataclass(repr=False)
class coopStageSchema(JSONDataClass):
    name: str
    id: str


@dataclass(repr=False)
class afterGradeSchema(JSONDataClass):
    name: str
    id: str


@dataclass(repr=False)
class myResultSchema(JSONDataClass):
    deliverCount: int
    goldenDeliverCount: int


@dataclass(repr=False)
class waveResultsNodeSchema(JSONDataClass):
    waveNumber: int


@dataclass(repr=False)
class coopHistoryDetailsNodeSchema(JSONDataClass):
    id: str
    weapons: list[weaponsNodeSchema]
    resultWave: int
    coopStage: coopStageSchema
    afterGrade: afterGradeSchema
    afterGradePoint: int
    gradePointDiff: str
    myResult: myResultSchema
    memberResults: list[myResultSchema]
    waveResults: list[waveResultsNodeSchema]
    bossResult: None = None
    nextHistoryDetail: nextHistoryDetailSchema = None
    previousHistoryDetail: previousHistoryDetailSchema = None


@dataclass(repr=False)
class coopHistoryDetailsSchema(JSONDataClass):
    nodes: list[coopHistoryDetailsNodeSchema]


@dataclass(repr=False)
class coopHistoryGroupsNodeSchema(JSONDataClass):
    startTime: str
    endTime: str
    mode: str
    rule: str
    highestResult: highestResultSchema
    historyDetails: coopHistoryDetailsSchema


@dataclass(repr=False)
class coopHistoryGroupsSchema(JSONDataClass):
    nodes: list[coopHistoryGroupsNodeSchema]


@dataclass(repr=False)
class CoopResultSchema(JSONDataClass):
    regularAverageClearWave: float
    regularGrade: RegularGradeSchema
    regularGradePoint: int
    monthlyGear: monthlyGearSchema
    scale: scaleSchema
    pointCard: pointCardSchema
    historyGroups: coopHistoryGroupsSchema
    historyGroupsOnlyFirst: historyGroupsOnlyFirstSchema
