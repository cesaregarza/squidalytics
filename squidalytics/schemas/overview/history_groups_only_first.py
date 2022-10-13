from dataclasses import dataclass

from squidalytics.schemas.base import JSONDataClass


@dataclass(repr=False)
class MaskingImageSchema(JSONDataClass):
    width: int
    height: int
    maskImageUrl: str
    overlayImageUrl: str


@dataclass(repr=False)
class SpecialWeaponSchema(JSONDataClass):
    maskingImage: MaskingImageSchema
    id: str


@dataclass(repr=False)
class WeaponSchema(JSONDataClass):
    specialWeapon: SpecialWeaponSchema
    id: str


@dataclass(repr=False)
class PlayerSchema(JSONDataClass):
    weapon: WeaponSchema
    id: str


@dataclass(repr=False)
class historyDetailsNodeSchema(JSONDataClass):
    player: PlayerSchema
    id: str


@dataclass(repr=False)
class historyDetailsSchema(JSONDataClass):
    nodes: list[historyDetailsNodeSchema]


@dataclass(repr=False)
class historyGroupsOnlyFirstNodesSchema(JSONDataClass):
    historyDetails: historyDetailsSchema


@dataclass(repr=False)
class historyGroupsOnlyFirstSchema(JSONDataClass):
    nodes: list[historyGroupsOnlyFirstNodesSchema]
