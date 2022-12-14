import re

import pandas as pd

first_pattern = re.compile(r"(.)([A-Z][a-z]+)")
second_pattern = re.compile(r"([a-z0-9])([A-Z])")


def flatten_dict(
    input_dict: dict, keep_path: bool = False, separator: str = "."
) -> dict:
    """Flatten a nested dictionary

    Args:
        input_dict (dict): Nested dictionary to flatten
        keep_path (bool): Keep the full path to the value or not. If True, the
            keys will be in the form of "a.b.c". Otherwise, the keys will be in
            the form of "c". Defaults to False.
        separator (str): The separator to use when joining the keys. Defaults to
            ".".

    Returns:
        dict: Flattened dictionary
    """

    def _flatten_dict(key: str, value: dict) -> dict:
        prepend_key = key + separator if keep_path else ""
        working_dict = {}
        for inner_key, inner_value in value.items():
            working_dict[prepend_key + inner_key] = inner_value
        return working_dict

    output_dict = {}

    for key, value in input_dict.items():
        if isinstance(value, dict):
            flattened_dict = flatten_dict(
                value, keep_path=keep_path, separator=separator
            )
            output_dict.update(_flatten_dict(key, flattened_dict))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                flattened_dict = flatten_dict(
                    item, keep_path=keep_path, separator=separator
                )
                prepend_key = key + separator + str(i) if keep_path else ""
                output_dict.update(_flatten_dict(prepend_key, flattened_dict))
        else:
            output_dict[key] = value
    return output_dict


def weapon_column_rename(column_name: str) -> str:
    """Renames the weapon column names from CamelCase to snake_case and prepends
    "weapon_" to the column name.

    Args:
        column_name (str): The column name to rename.

    Returns:
        str: The renamed column name.
    """
    # https://stackoverflow.com/a/1176023/12507525
    # This function is for efficiency, since the patterns are compiled only once
    column_name = first_pattern.sub(r"\1_\2", column_name)
    column_name = second_pattern.sub(r"\1_\2", column_name).lower()
    return "weapon_" + column_name


def aggregate_masking(*masks: pd.Series, operation: str = "and") -> pd.Series:
    """Aggregate multiple masks into a single mask, given an operation to
        aggregate. Assumes all masks have the same index and length.

    Args:
        *masks (pd.Series): The masks to aggregate.
        operation (str): The operation to aggregate the masks with. Only accepts
            "and", or "or". Defaults to "and".

    Raises:
        ValueError: If the operation is not "and" or "or".

    Returns:
        pd.Series: The aggregated mask.
    """
    if operation == "and":
        aggregate_mask = pd.Series(True, index=masks[0].index)
        for mask in masks:
            aggregate_mask &= mask
    elif operation == "or":
        aggregate_mask = pd.Series(False, index=masks[0].index)
        for mask in masks:
            aggregate_mask |= mask
    else:
        raise ValueError("Invalid operation")
    return aggregate_mask
