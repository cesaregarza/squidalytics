from typing import Any


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
