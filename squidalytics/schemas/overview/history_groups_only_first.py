from dataclasses import dataclass

from squidalytics.schemas.base import JSONDataClass


@dataclass
class MaskingImageSchema(JSONDataClass):
    width: int
    height: int
    maskImageUrl: str
    overlayImageUrl: str


@dataclass
class SpecialWeaponSchema(JSONDataClass):
    maskingImage: MaskingImageSchema
    id: str


@dataclass
class WeaponSchema(JSONDataClass):
    specialWeapon: SpecialWeaponSchema
    id: str


@dataclass
class PlayerSchema(JSONDataClass):
    weapon: WeaponSchema
    id: str


@dataclass
class historyGroupsOnlyFirstSchema(JSONDataClass):
    nodes: list[PlayerSchema]
