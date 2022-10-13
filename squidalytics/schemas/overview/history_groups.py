from dataclasses import dataclass

from squidalytics.schemas.base import JSONDataClass


@dataclass
class vsModeSchema(JSONDataClass):
    mode: str
    id: str


@dataclass
class vsRuleSchema(JSONDataClass):
    name: str
    id: str


@dataclass
class vsStageImageSchema(JSONDataClass):
    url: str


@dataclass
class vsStageSchema(JSONDataClass):
    image: vsStageImageSchema
    name: str
    id: str


@dataclass
class weaponImageSchema(JSONDataClass):
    url: str


@dataclass
class weaponSchema(JSONDataClass):
    image: weaponImageSchema
    name: str
    id: str


@dataclass
class playerSchema(JSONDataClass):
    weapon: weaponSchema
    id: str


@dataclass
class myTeamResultSchema(JSONDataClass):
    paintPoint: int = None
    paintRatio: float = None
    score: int = None

    def which(self) -> str:
        if self.score is not None:
            return "anarchy"
        elif (self.paintPoint is not None) and (self.paintRatio is not None):
            return "regular"
        else:
            pass


@dataclass
class myTeamSchema(JSONDataClass):
    result: myTeamResultSchema


@dataclass
class bankaraMatchSchema(JSONDataClass):
    earnedUdemaePoint: None = None


@dataclass
class nextHistoryDetailSchema(JSONDataClass):
    id: str


@dataclass
class previousHistoryDetailSchema(JSONDataClass):
    id: str


@dataclass
class baseHistoryDetailsNodesSchema(JSONDataClass):
    id: str
    vsMode: vsModeSchema
    vsRule: vsRuleSchema
    vsStage: vsStageSchema
    judgement: str
    player: playerSchema
    myTeam: myTeamSchema
    knockout: str


@dataclass
class anarchyHistoryDetailsNodesSchema(baseHistoryDetailsNodesSchema):
    bankaraMatch: bankaraMatchSchema
    udemae: str
    nextHistoryDetail: nextHistoryDetailSchema = None
    previousHistoryDetail: previousHistoryDetailSchema = None


@dataclass
class regularHistoryDetailsNodesSchema(baseHistoryDetailsNodesSchema):
    playedTime: str
    nextHistoryDetail: nextHistoryDetailSchema = None
    previousHistoryDetail: previousHistoryDetailSchema = None


@dataclass
class anarchyHistoryDetailsSchema(JSONDataClass):
    nodes: list[anarchyHistoryDetailsNodesSchema]


@dataclass
class regularHistoryDetailsSchema(JSONDataClass):
    nodes: list[regularHistoryDetailsNodesSchema]


@dataclass
class bankaraMatchChallengeSchema(JSONDataClass):
    winCount: int
    loseCount: int
    maxWinCount: int
    maxLoseCount: int
    state: str
    isPromo: bool
    isUdemaeUp: bool
    udemaeAfter: str
    earnedUdemaePoint: int


@dataclass
class anarchyHistoryGroupsNodesSchema(JSONDataClass):
    bankaraMatchChallenge: bankaraMatchChallengeSchema
    historyDetails: anarchyHistoryDetailsSchema


@dataclass
class regularHistoryGroupsNodesSchema(JSONDataClass):
    historyDetails: regularHistoryDetailsSchema


@dataclass
class anarchyHistoryGroupsSchema(JSONDataClass):
    nodes: list[anarchyHistoryGroupsNodesSchema]


@dataclass
class regularHistoryGroupsSchema(JSONDataClass):
    nodes: list[regularHistoryGroupsNodesSchema]
