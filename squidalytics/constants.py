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


WEAPON_MAP = WeaponReference()
