import re

first_pattern = re.compile(r"(.)([A-Z][a-z]+)")
second_pattern = re.compile(r"([a-z0-9])([A-Z])")


def flatten_dict(
    input_dict: dict, keep_path: bool = False, separator: str = "."
) -> dict:
    """Flatten a nested dictionary

    Args:
        input_dict (dict): Nested dictionary to flatten
        keep_path (bool, optional): Keep the full path to the value or not.
            If True, the keys will be in the form of "a.b.c". Otherwise, the
            keys will be in the form of "c". Defaults to False.

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
    # This function is for efficiency, since the patterns are compiled only once
    column_name = first_pattern.sub(r"\1_\2", column_name)
    column_name = second_pattern.sub(r"\1_\2", column_name).lower()
    return "weapon_" + column_name
