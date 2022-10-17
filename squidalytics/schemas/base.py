from dataclasses import is_dataclass
from typing import Any, Callable, Type, cast


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
            TypeError: If the annotation is not a dataclass.
            SecondaryException: If the key of the dictionary is not found in the
                result of the get_annotations() method.
            Exception: SecondaryExceptions get passed up the chain.
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
        """Print the object tree in a human readable format.

        Args:
            level (int, optional): The level of the object tree. Defaults to 1.

        Returns:
            str: The object tree in a human readable format.
        """
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
                except TypeError:
                    # If list contains None, then the above will fail.
                    out += tabs + "  " + value[idx].__repr__() + "\n"
            else:
                out += tabs + f"{key}: {type(value).__name__}\n"
        return out

    def __getitem__(
        self, key: str | int | slice | tuple[str | int, ...]
    ) -> Any:
        """Get the value of the given key. If the key is a tuple, then enable
        numpy style indexing.

        Args:
            key (str | tuple[str  |  int]): The key to get the value of.

        Raises:
            IndexError: If the key is an integer or slice and there is more than
                one item in the object tree.

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
                    if isinstance(item, JSONDataClass):
                        id_index.update(**item.__index_ids())
            elif key == "id":
                id_index[str(value)] = self
        return id_index

    def search_by_id(self, id: int | str) -> Any:
        """Search the object tree for the object with the given id. Indexing is
        done on the first call to this method, and then the generated index is
        used for subsequent calls.

        Args:
            id (str): The id of the object to search for. If fed an integer,
                it will be converted to a string.

        Returns:
            Any: The object with the given id.
        """
        if getattr(self, "__id_index", None) is None:
            self.__id_index = self.__index_ids()
        return self.__id_index[str(id)]

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
                    if isinstance(item, JSONDataClass):
                        item.traverse_tree(func)
            else:
                func(self)

    def top_level_keys(self) -> list[str]:
        """Get the top level keys of the object tree.

        Returns:
            list[str]: The top level keys of the object tree.
        """
        return list(self.__dict__.keys())


class JSONDataClassListTopLevel(JSONDataClass):
    """A subclass of JSONDataClass that has a specific override for the __init__
    method to allow for the top level of the object tree to be a list. This is
    an abstract base class and should not be instantiated directly.
    """

    next_level_type: Type[JSONDataClass] = JSONDataClass

    def __new__(cls, *args, **kwargs):
        """Override the __new__ method to ensure that making the class into a
        dataclass is not allowed.
        """
        if is_dataclass(cls):
            raise TypeError(
                "JSONDataClassListTopLevel should not be used as a dataclass."
            )
        return super().__new__(cls)

    def __init__(self, json: list[dict] | list[Type[next_level_type]]) -> None:
        """Override the __init__ method to allow for the top level of the object
        tree to be a list.

        Args:
            json (list[dict] | list[Type[next_level_type]]): The json to
                convert to an object tree. Should be a list of dictionaries, or
                a list of objects of the next level type.

        Raises:
            TypeError: If the types of the items in the list are not all that of
                the defined next level type.
        """
        if len(json) > 0 and all(isinstance(result, dict) for result in json):
            self.data = [self.next_level_type(**result) for result in json]
        elif not all(
            isinstance(result, self.next_level_type) for result in json
        ):
            raise TypeError(
                "All items in the list must be of type "
                f"{self.next_level_type.__name__}"
            )
        else:
            self.data = json

    def __getitem__(
        self, key: str | int | slice | tuple[str | int, ...]
    ) -> Any:
        """Get the value of the given key. If the key is a tuple, then enable
        numpy style indexing. To maintain liskov substitution, this method
        will return an error if the first or only key are strings.

        Args:
            key (str | int | slice | tuple[str  |  int, ...]): The key to get
                the value of.

        Raises:
            TypeError: If the key is a string.
            TypeError: If the key is a tuple and the first key is a string.

        Returns:
            Any: The value of the given key.
        """
        if isinstance(key, tuple):
            first_index = key[0]
            other_index = key[1:]
            if isinstance(first_index, str):
                raise TypeError("Cannot index top level by string")
            return self.data[first_index][other_index]
        elif isinstance(key, slice):
            return JSONDataClassListTopLevel(self.data[key])
        elif isinstance(key, str):
            raise TypeError("Cannot index top level by string")
        return self.data[key]

    def __getattr__(self, key: str) -> Any:
        """If the attribute exists, act normally. Otherwise, assume the
        attribute exists in the top level child, data, and return a function
        that returns that attribute for each node.

        Args:
            key (str): Attribute name

        Returns:
            Any: If the attribute exists, return the attribute. Otherwise,
            return a function that returns the attribute for each node.
        """
        try:
            return super().__getattr__(key)
        except AttributeError:
            pass

        if key == "__id_index":
            if key in self.__dict__:
                return self.__dict__[key]
            else:
                return None

        def attr_func(*args, **kwargs) -> list[Any]:
            return [getattr(node, key)(*args, **kwargs) for node in self.data]

        return attr_func
