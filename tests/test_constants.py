import pytest

from squidalytics.constants import WEAPON_MAP, WeaponReference


class TestWeaponReference:
    @pytest.mark.internet
    def test_versus_weapons(self) -> None:
        weapon_map = WeaponReference()
        assert weapon_map._versus_weapons is None
        assert weapon_map.versus_weapons is not None
        assert weapon_map._versus_weapons is not None

    @pytest.mark.internet
    def test_weapon_classes(self) -> None:
        weapons = WEAPON_MAP.versus_weapon_names
        assert isinstance(weapons, list)
        assert len(weapons) > 0
        assert all(isinstance(x, str) for x in weapons)

    @pytest.mark.internet
    def test_weapon_names_by_class(self) -> None:
        weapons = WEAPON_MAP.weapon_names_by_class("shooter")
        assert isinstance(weapons, list)
        assert len(weapons) > 0
        assert all(isinstance(x, str) for x in weapons)

    @pytest.mark.internet
    def test_classify_string(self) -> None:
        assert WEAPON_MAP.classify_string("shooter") == "class"
        assert WEAPON_MAP.classify_string("splattershot jr.") == "weapon"
        assert WEAPON_MAP.classify_string("fail") == ""

    @pytest.mark.internet
    def test_parse_input(self) -> None:
        weapons, classes = WEAPON_MAP.parse_input("shooter")
        assert isinstance(weapons, list)
        assert isinstance(classes, list)
        assert len(weapons) > 0
        assert len(classes) == 1
        assert all(isinstance(x, str) for x in weapons)
        assert all(isinstance(x, str) for x in classes)
        assert classes[0] == "shooter"

        weapons, classes = WEAPON_MAP.parse_input(["shooter", "splatterscope"])
        assert isinstance(weapons, list)
        assert isinstance(classes, list)
        assert len(weapons) > 0
        assert len(classes) == 1
        assert all(isinstance(x, str) for x in weapons)
        assert all(isinstance(x, str) for x in classes)
        assert classes[0] == "shooter"

        with pytest.raises(ValueError):
            WEAPON_MAP.parse_input("fail")
