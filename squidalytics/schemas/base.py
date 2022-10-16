from typing import Any, Callable, cast, TypeVar, Type


class SecondaryException(Exception):
    pass


class JSONDataClass:
    """Base class for all dataclasses. This class provides the following
    functionality:
    - Recursively initialize dataclasses from dictionaries.
    - Print the object tree in a human readable format.
    - Enable numpy style indexing, e.g. obj["key1", "key2"].
    - Index all the ids in the object tree.
    - Get the top level keys of the object tree.
    - Provide a method to apply a function to all the objects in the object.
    """

    def __post_init__(self) -> None:
        """After initializing the dataclass, check if any of the fields are
        dictionaries. If so, initialize the corresponding annotation with the
        dictionary as the argument.

        Raises:
            SecondaryException: If the key of the dictionary is not found in the
                result of the get_annotations() method.
            e: SecondaryExceptions get passed up the chain.
        """
        # This class should be used as a base class for all dataclasses
        for key, value in self.__dict__.items():

            try:
                if isinstance(value, dict):
                    annotations = self.get_annotations()
                    cls = annotations[key]
                    # This is a hack to get around the fact that there is a key
                    # in the JSON that has a double underscore prefix. Since
                    # double underscore triggers name mangling,
                    # we circumvent that by using a single underscore prefix in
                    # dataclass definition instead, and then replacing the
                    # double underscore with a single underscore here.
                    value = {k.replace("__", "_"): v for k, v in value.items()}
                    setattr(self, key, cls(**value))
                elif (
                    isinstance(value, list)
                    and (len(value) > 0)
                    and isinstance(value[0], dict)
                ):
                    annotations = self.get_annotations()
                    super_cls = annotations[key]
                    # Try/except block to catch the case where the list is
                    # empty.
                    try:
                        cls = super_cls.__args__[0]
                    except AttributeError:
                        setattr(self, key, [])
                        continue
                    # Replace double underscores with single underscores for
                    # the same reason as above.
                    attrset = [
                        cls(
                            **{k.replace("__", "_"): v for k, v in item.items()}
                        )
                        for item in value
                    ]
                    setattr(self, key, attrset)
            except Exception as e:
                if not isinstance(e, SecondaryException):
                    # print(f"key: {keyval}, value: {value}")
                    raise SecondaryException from e
                else:
                    raise e

    @classmethod
    def get_annotations(cls) -> dict[str, Type[Any]]:
        """Get the annotations of the class, but also include the annotations
        of any ancestor classes.

        Returns:
            dict[str, type]: A dictionary of the annotations of the class and
                the annotations of any ancestor classes.
        """
        annotations: dict[str, Any] = {}
        for c in cls.mro():
            try:
                annotations.update(**c.__annotations__)
            except AttributeError:
                pass
        return annotations

    def __repr__(self, level=1) -> str:
        """Print the object tree in a human readable format."""
        out = self.__class__.__name__ + ":\n" if level == 1 else ""
        tabs = " " * level

        for key, value in self.__dict__.items():
            if isinstance(value, JSONDataClass):
                out += f"{tabs}{key}:\n" + value.__repr__(level + 1)
            elif isinstance(value, list):
                if len(value) == 0:
                    out += f"{tabs}{key}: list[]\n"
                    continue
                idx = 1 if len(value) > 1 else 0
                out += (
                    tabs
                    + f"{key}: "
                    + f"list[{value[idx].__class__.__name__}]\n"
                )
                # Assume all items in the list are of the same type
                try:
                    out += value[idx].__repr__(level + 1)
                except TypeError as e:
                    # If list contains None, then the above will fail.
                    out += value[idx].__repr__() + "\n"
            else:
                out += tabs + f"{key}: {type(value).__name__}\n"
        return out

    def __getitem__(self, key: str | int | slice | tuple[str | int, ...]) -> Any:
        """Get the value of the given key. If the key is a tuple, then enable
        numpy style indexing.

        Args:
            key (str | tuple[str  |  int]): The key to get the value of.

        Returns:
            Any: The value of the given key.
        """
        if isinstance(key, str):
            return getattr(self, key)
        elif isinstance(key, (int, slice)):
            top_level_keys = self.top_level_keys()
            if len(top_level_keys) > 1:
                raise IndexError(
                    "Cannot index with an integer or slice if there are "
                    "multiple top level keys."
                )
            return getattr(self, top_level_keys[0])[key]

        # If the key is a tuple, recursively call __getitem__ on the
        # corresponding attribute.
        curent_level = self
        for k in key:
            curent_level = curent_level[k]

        return curent_level

    def __index_ids(self) -> dict[str, Any]:
        """Index all the ids in the object tree. This is used to get the
        corresponding object from the id.

        Returns:
            dict[str, Any]: A dictionary of all the ids in the object tree.
        """
        id_index: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if isinstance(value, JSONDataClass):
                id_index.update(**value.__index_ids())
            elif isinstance(value, list):
                for item in value:
                    item = cast(JSONDataClass, item)
                    id_index.update(**item.__index_ids())
            elif key == "id":
                id_index[value] = self
        return id_index

    def search_by_id(self, id: str) -> Any:
        """Search the object tree for the object with the given id. Indexing is
        done on the first call to this method, and then the generated index is
        used for subsequent calls.

        Args:
            id (str): The id of the object to search for.

        Returns:
            Any: The object with the given id.
        """
        if getattr(self, "__id_index", None) is None:
            self.__id_index = self.__index_ids()
        return self.__id_index[id]

    def traverse_tree(self, func: Callable[[Any], Any]) -> None:
        """Traverse the object tree and apply the given function to each object.

        Args:
            func (Callable[[Any], Any]): The function to apply to each object.
        """
        for key, value in self.__dict__.items():
            if isinstance(value, JSONDataClass):
                value.traverse_tree(func)
            elif isinstance(value, list):
                for item in value:
                    item = cast(JSONDataClass, item)
                    item.traverse_tree(func)
            else:
                func(self)

    def top_level_keys(self) -> list[str]:
        """Get the top level keys of the object tree.

        Returns:
            list[str]: The top level keys of the object tree.
        """
        return list(self.__dict__.keys())
