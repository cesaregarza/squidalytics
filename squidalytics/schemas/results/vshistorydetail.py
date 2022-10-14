from dataclasses import dataclass

from squidalytics.schemas.base import JSONDataClass
from squidalytics.schemas.general import (
    colorSchema,
    idSchema,
    imageSchema,
    vsModeSchema,
    vsRuleSchema,
    vsStageSchema,
    weaponSchema,
)
from squidalytics.constants import (
    PRIMARY_ONLY,
    ABILITIES,
    ALL_ABILITIES,
)


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

    def calculate_abilities(self) -> dict[str, int]:
        abilities = {ability: 0 for ability in ALL_ABILITIES}
        for gear in [self.headGear, self.clothingGear, self.shoesGear]:
            gear_abilities = gear.calculate_abilities()
            for ability, value in gear_abilities.items():
                abilities[ability] += value
        return abilities


@dataclass(repr=False)
class playerFullSchema(playerSchema):
    isMyself: bool
    species: str
    festDragonCert: str
    _typename: str
    weapon: weaponSchema
    result: resultSchema = None


@dataclass(repr=False)
class teamSchema(JSONDataClass):
    color: colorSchema
    judgement: str
    players: list[playerFullSchema]
    order: int
    result: resultSchema = None
    tricolorRole: str = None
    festTeamName: str = None


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


@dataclass(repr=False)
class battleSchema(JSONDataClass):
    vsHistoryDetail: vsHistoryDetailSchema
