from dataclasses import dataclass

from squidalytics.schemas.base import JSONDataClass


@dataclass(repr=False)
class idSchema(JSONDataClass):
    id: str


@dataclass(repr=False)
class vsModeSchema(JSONDataClass):
    mode: str
    id: str


@dataclass(repr=False)
class vsRuleSchema(JSONDataClass):
    name: str
    id: str
    rule: str = None


@dataclass(repr=False)
class imageSchema(JSONDataClass):
    url: str


@dataclass(repr=False)
class vsStageSchema(JSONDataClass):
    image: imageSchema
    name: str
    id: str


@dataclass(repr=False)
class colorSchema(JSONDataClass):
    r: float
    g: float
    b: float
    a: float


@dataclass(repr=False)
class maskingImageSchema(JSONDataClass):
    height: int
    width: int
    maskImageUrl: str
    overlayImageUrl: str


@dataclass(repr=False)
class specialWeaponSchema(JSONDataClass):
    maskingImage: maskingImageSchema
    id: str
    name: str
    image: imageSchema


@dataclass(repr=False)
class subWeaponSchema(JSONDataClass):
    id: str
    name: str
    image: imageSchema


@dataclass(repr=False)
class weaponSchema(JSONDataClass):
    name: str
    image: imageSchema
    specialWeapon: specialWeaponSchema
    id: str
    image3d: imageSchema
    image2d: imageSchema
    image3dThumbnail: imageSchema
    image2dThumbnail: imageSchema
    subWeapon: subWeaponSchema
