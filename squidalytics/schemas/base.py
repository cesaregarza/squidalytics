from dataclasses import dataclass


class SecondaryException(Exception):
    pass


class JSONDataClass:
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
            # This is a hack to get around the fact that there is a key in the
            # JSON that has a double underscore prefix. Since double underscore
            # triggers name mangling, we circumvent that by using a single
            # underscore prefix in dataclass definition instead, and then
            # replacing it with a double underscore here.
            if key[0] == "_":
                keyval = "_" + key
            else:
                keyval = key

            try:
                if isinstance(value, dict):
                    annotations = self.get_annotations()
                    cls = annotations[keyval]
                    # print(f"cls: {cls.__name__}, key: {keyval}")
                    setattr(self, keyval, cls(**value))
                elif (
                    isinstance(value, list)
                    and (len(value) > 0)
                    and isinstance(value[0], dict)
                ):
                    annotations = self.get_annotations()
                    super_cls = annotations[keyval]
                    cls = super_cls.__args__[0]
                    # print(
                    #     f"super_cls: {super_cls.__name__}, "
                    #     + f"cls: {cls.__name__}, "
                    #     + f"key: {keyval}"
                    # )
                    setattr(self, keyval, [cls(**item) for item in value])
            except Exception as e:
                if not isinstance(e, SecondaryException):
                    # print(f"key: {keyval}, value: {value}")
                    raise SecondaryException from e
                else:
                    raise e

    @classmethod
    def get_annotations(cls) -> dict[str, type]:
        """Get the annotations of the class, but also include the annotations
        of any ancestor classes.

        Returns:
            dict[str, type]: A dictionary of the annotations of the class and
                the annotations of any ancestor classes.
        """
        annotations = {}
        for c in cls.mro():
            try:
                annotations.update(**c.__annotations__)
            except AttributeError:
                pass
        return annotations
