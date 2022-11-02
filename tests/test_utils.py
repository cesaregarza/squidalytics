import pandas as pd
import pandas.testing as pdt
import pytest

from squidalytics.utils import (
    aggregate_masking,
    flatten_dict,
    weapon_column_rename,
)


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


def test_aggregate_masking() -> None:
    mask1 = pd.Series([True, False, True, False])
    mask2 = pd.Series([True, True, False, False])
    mask3 = pd.Series([True, False, False, False])
    expected_and = pd.Series([True, False, False, False])
    expected_or = pd.Series([True, True, True, False])
    and_series = aggregate_masking(mask1, mask2, mask3, operation="and")
    or_series = aggregate_masking(mask1, mask2, mask3, operation="or")
    pdt.assert_series_equal(and_series, expected_and)
    pdt.assert_series_equal(or_series, expected_or)
    with pytest.raises(ValueError):
        aggregate_masking(mask1, mask2, mask3, operation="fail")
