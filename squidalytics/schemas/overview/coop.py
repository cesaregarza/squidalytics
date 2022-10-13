from dataclasses import dataclass

from squidalytics.schemas.base import JSONDataClass
from squidalytics.schemas.overview.history_groups import (
    nextHistoryDetailSchema,
    previousHistoryDetailSchema,
    weaponImageSchema,
)


@dataclass
class RegularGradeSchema(JSONDataClass):
    name: str
    id: str


@dataclass
class monthlyGearSchema(JSONDataClass):
    _typename: str
    name: str
    image: weaponImageSchema


@dataclass
class scaleSchema(JSONDataClass):
    gold: int
    silver: int
    bronze: int


@dataclass
class pointCardSchema(JSONDataClass):
    defeatBossCount: int
    deliverCount: int
    goldenDeliverCount: int
    playCount: int
    rescueCount: int
    regularPoint: int
    totalPoint: int


@dataclass
class gradeSchema(JSONDataClass):
    name: str
    id: str


@dataclass
class highestResultSchema(JSONDataClass):
    grade: gradeSchema
    gradePoint: int
    jobScore: int


@dataclass
class weaponsNodeSchema(JSONDataClass):
    name: str
    image: weaponImageSchema


@dataclass
class coopStageSchema(JSONDataClass):
    name: str
    id: str


@dataclass
class afterGradeSchema(JSONDataClass):
    name: str
    id: str


@dataclass
class myResultSchema(JSONDataClass):
    deliverCount: int
    goldenDeliverCount: int


@dataclass
class waveResultsNodeSchema(JSONDataClass):
    waveNumber: int


@dataclass
class coopHistoryNodeDetails(JSONDataClass):
    id: str
    weapons: list[weaponsNodeSchema]
    resultWave: int
    coopStage: coopStageSchema
    afterGrade: afterGradeSchema
    gradePointDiff: str
    myResult: myResultSchema
    memberResults: list[myResultSchema]
    waveResults: list[waveResultsNodeSchema]
    bossResult: None = None
    nextHistoryDetail: nextHistoryDetailSchema | None = None
    previousHistoryDetail: previousHistoryDetailSchema | None = None


@dataclass
class coopHistoryGroupsNodeSchema(JSONDataClass):
    startTime: str
    endTime: str
    mode: str
    rule: str
    highestResult: highestResultSchema
