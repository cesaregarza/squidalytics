from functools import cached_property
from typing import Any

from squidalytics.data.scrape_leanny import (
    WeaponsMap,
    enumerate_versions,
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
    def __init__(
        self, version: str | None = None, language: str = "USen"
    ) -> None:
        self._versus_weapons: WeaponsMap | None = None
        self._coop_weapons: WeaponsMap | None = None
        self._version = version
        self._lang = language

    @cached_property
    def versus_weapons(self) -> WeaponsMap:
        if self._versus_weapons is None:
            self._versus_weapons = get_versus_weapons_simplified(
                version=self._version, lang=self._lang
            )
        return self._versus_weapons

    @property
    def versus_weapon_names(self) -> list[str]:
        return [x.lower() for x in self.versus_weapons.keys()]

    @cached_property
    def weapon_classes(self) -> list[str]:
        return set(x["Class"].lower() for x in self.versus_weapons.values())

    def weapon_names_by_class(self, weapon_class: str | list[str]) -> list[str]:
        """Return a list of weapon names for a given weapon class. If given a
        list of classes, return a list of all weapons in those classes. Does not
        separate by class.

        Args:
            weapon_class (str | list[str]): The weapon class to get names for.

        Returns:
            list[str]: A list of weapon names.
        """
        if isinstance(weapon_class, str):
            weapon_class = [weapon_class]
        weapon_class = [x.lower() for x in weapon_class]

        out = []
        for weapon in self.versus_weapons.values():
            if weapon["Class"].lower() in weapon_class:
                out.append(weapon["Name"].lower())
        return out

    def classify_string(self, string: str) -> str:
        """Classify a string as a weapon, ability, or other.

        Args:
            string (str): The string to classify.

        Returns:
            str: The classification.
        """
        string = string.lower()
        if string in self.weapon_classes:
            return "class"
        elif string in self.versus_weapon_names:
            return "weapon"
        else:
            return ""

    def parse_input(
        self, input_: str | list[str]
    ) -> tuple[list[str], list[str]]:
        """Parse a string or list of strings into a list of weapon names.

        Args:
            input_ (str | list[str]): The string or list of strings to parse.

        Raises:
            ValueError: If the input is not recognized

        Returns:
            tuple:
                list[str]: A list of weapon names.
                list[str]: A list of weapon classes.
        """
        if isinstance(input_, str):
            input_ = [input_]
        input_ = [x.lower() for x in input_]

        weapons_list = []
        classes_list = []
        for item in input_:
            classify = self.classify_string(item)
            if classify == "class":
                weapons_list.extend(self.weapon_names_by_class(item))
                classes_list.append(item)
            elif classify == "weapon":
                weapons_list.append(item)
            else:
                raise ValueError(f"Invalid input: {item}")
        return weapons_list, classes_list


class SuperWeaponReference:
    """A class to hold references to all weapon data for all versions of the
    game. If a version is not specified, the latest version is used. If a child
    attribute is called without a version, the latest version is used.
    """

    def __init__(self, preferred_version: str | None = None) -> None:
        self._storage = {}
        self.existing_versions = enumerate_versions()
        if preferred_version is None:
            preferred_version = max(self.existing_versions)
        else:
            preferred_version = self.__parse_version(preferred_version)
        self.preferred_version = preferred_version
        self.create_reference(preferred_version)

    def __parse_version(self, version: str) -> str:
        return version.replace(".", "").replace("v", "")

    def create_reference(self, version: str, language: str = "USen") -> None:
        version = self.__parse_version(version)
        if version not in self._storage:
            self._storage[version] = WeaponReference(version, language)

    def __getitem__(self, version: str) -> WeaponReference:
        version = self.__parse_version(version)
        if version not in self._storage:
            self.create_reference(version)
        return self._storage[version]

    def __getattr__(self, name: str) -> Any:
        """If a child attribute is called without a version, use the preferred
        version. If SuperWeaponReference and WeaponReference both share an
        attribute, the SuperWeaponReference attribute is preferred. This allows
        backwards compatibility without breaking everything.

        Args:
            name (str): The attribute name.
        
        Raises:
            AttributeError: If the attribute is not found in either class.

        Returns:
            Any: The attribute value.
        """
        if name in self.__dict__:
            return self.__dict__[name]
        # To prevent infinite recursion, check if the attribute exists in the
        # preferred version first.
        weapon_reference = self[self.preferred_version]
        if name in weapon_reference.__dict__ or hasattr(weapon_reference, name):
            return weapon_reference.__getattribute__(name)
        else:
            raise AttributeError(
                "Neither SuperWeaponReference nor WeaponReference have an "
                f"attribute named '{name}'."
            )


WEAPON_MAP = SuperWeaponReference()
