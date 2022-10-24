import pytest

from squidalytics.utils import flatten_dict, weapon_column_rename


def test_flatten_dict() -> None:
    input_dict = {"a": {"b": [{"c": 1, "d": 2}, {"c": 3, "d": 4}]}}
    expected_dict_false = {"c": 3, "d": 4}
    assert flatten_dict(input_dict) == expected_dict_false
    expected_dict_true = {
        "a.b.0.c": 1,
        "a.b.0.d": 2,
        "a.b.1.c": 3,
        "a.b.1.d": 4,
    }
    assert flatten_dict(input_dict, keep_path=True) == expected_dict_true


@pytest.mark.parametrize(
    "input_str, expected_str",
    [
        ("a", "a"),
        ("AB", "ab"),
        ("aB", "a_b"),
        ("aBc", "a_bc"),
        ("abC", "ab_c"),
        ("aBcD", "a_bc_d"),
        ("aBCd", "a_b_cd"),
        ("aBCDe", "a_bc_de"),
    ],
)
def test_weapon_column_rename(input_str: str, expected_str: str) -> None:
    assert weapon_column_rename(input_str) == ("weapon_" + expected_str)
