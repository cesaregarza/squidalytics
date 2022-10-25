from functools import cached_property

from squidalytics.data.scrape_leanny import (
    WeaponsMap,
    get_versus_weapons_simplified,
)

PRIMARY_ONLY = [
    "Comeback",
    "Last-Ditch Effort",
    "Opening Gambit",
    "Tenacity",
    "Ability Doubler",
    "Haunt",
    "Ninja Squid",
    "Respawn Punisher",
    "Thermal Ink",
    "Drop Roller",
    "Object Shredder",
    "Stealth Jump",
]

ABILITIES = [
    "Ink Saver (Main)",
    "Ink Saver (Sub)",
    "Ink Recovery Up",
    "Run Speed Up",
    "Swim Speed Up",
    "Special Charge Up",
    "Special Saver",
    "Special Power Up",
    "Quick Respawn",
    "Quick Super Jump",
    "Sub Power Up",
    "Ink Resistance Up",
    "Sub Resistance Up",
    "Intensify Action",
]

ALL_ABILITIES = PRIMARY_ONLY + ABILITIES


class WeaponReference:
    def __init__(self) -> None:
        self._versus_weapons: WeaponsMap | None = None
        self._coop_weapons: WeaponsMap | None = None

    @cached_property
    def versus_weapons(self) -> WeaponsMap:
        if self._versus_weapons is None:
            self._versus_weapons = get_versus_weapons_simplified()
        return self._versus_weapons


WEAPON_MAP = WeaponReference()
