import pytest

from squidalytics.constants import SuperWeaponReference, WeaponReference


class TestWeaponReference:

    WEAPON_MAP = WeaponReference()

    @pytest.mark.internet
    def test_versus_weapons(self) -> None:
        weapon_map = WeaponReference()
        assert weapon_map._versus_weapons is None
        assert weapon_map.versus_weapons is not None
        assert weapon_map._versus_weapons is not None

    @pytest.mark.internet
    def test_weapon_classes(self) -> None:
        weapons = self.WEAPON_MAP.versus_weapon_names
        assert isinstance(weapons, list)
        assert len(weapons) > 0
        assert all(isinstance(x, str) for x in weapons)

    @pytest.mark.internet
    def test_weapon_names_by_class(self) -> None:
        weapons = self.WEAPON_MAP.weapon_names_by_class("shooter")
        assert isinstance(weapons, list)
        assert len(weapons) > 0
        assert all(isinstance(x, str) for x in weapons)

    @pytest.mark.internet
    def test_classify_string(self) -> None:
        assert self.WEAPON_MAP.classify_string("shooter") == "class"
        assert self.WEAPON_MAP.classify_string("splattershot jr.") == "weapon"
        assert self.WEAPON_MAP.classify_string("fail") == ""

    @pytest.mark.internet
    def test_parse_input(self) -> None:
        weapons, classes = self.WEAPON_MAP.parse_input("shooter")
        assert isinstance(weapons, list)
        assert isinstance(classes, list)
        assert len(weapons) > 0
        assert len(classes) == 1
        assert all(isinstance(x, str) for x in weapons)
        assert all(isinstance(x, str) for x in classes)
        assert classes[0] == "shooter"

        weapons, classes = self.WEAPON_MAP.parse_input(
            ["shooter", "splatterscope"]
        )
        assert isinstance(weapons, list)
        assert isinstance(classes, list)
        assert len(weapons) > 0
        assert len(classes) == 1
        assert all(isinstance(x, str) for x in weapons)
        assert all(isinstance(x, str) for x in classes)
        assert classes[0] == "shooter"

        with pytest.raises(ValueError):
            self.WEAPON_MAP.parse_input("fail")


class TestSuperWeaponReference:
    @pytest.mark.internet
    def test_init(self) -> None:
        swr = SuperWeaponReference()
        assert len(swr._storage) == 1
        swr = SuperWeaponReference("v1.0.0")
        assert len(swr._storage) == 1
        assert swr.preferred_version == "100"

    WEAPON_MAP = SuperWeaponReference()

    @pytest.mark.internet
    def test_create_reference(self) -> None:
        swr = SuperWeaponReference()
        assert len(swr._storage) == 1
        swr.create_reference("v1.0.0")
        assert len(swr._storage) == 2
        assert "100" in swr._storage

    @pytest.mark.internet
    def test_getitem(self) -> None:
        swr = SuperWeaponReference()
        assert len(swr._storage) == 1
        swr["v1.0.0"]
        assert len(swr._storage) == 2
        assert "100" in swr._storage

    @pytest.mark.internet
    def test_getattr(self) -> None:
        swr = SuperWeaponReference("v1.1.1")
        assert len(swr._storage) == 1
        # SuperWeaponReference attribute
        swr.create_reference("v1.0.0")
        assert len(swr._storage) == 2
        assert "100" in swr._storage
        # WeaponReference attribute
        assert swr.classify_string("shooter") == "class"
        # Non-existent attribute
        with pytest.raises(AttributeError):
            swr.fail
