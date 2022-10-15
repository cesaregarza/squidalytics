from dataclasses import dataclass
from typing import Any

from squidalytics.schemas.base import JSONDataClass
from squidalytics.schemas.results.vshistorydetail import battleSchema


@dataclass(repr=False)
class resultNodeSchema(JSONDataClass):
    data: battleSchema


class ResultsSchema(JSONDataClass):
    def __init__(self, json: list[dict]) -> None:
        try:
            self.data = [resultNodeSchema(**result) for result in json]
        except TypeError as e:
            if not all(isinstance(result, resultNodeSchema) for result in json):
                raise e
            self.data = json

    def __getitem__(self, key: int | slice | tuple[str | int]) -> Any:
        if isinstance(key, tuple):
            first_index = key[0]
            other_index = key[1:]
            return self.data[first_index][other_index]
        elif isinstance(key, slice):
            return ResultsSchema(self.data[key])
        return self.data[key]
