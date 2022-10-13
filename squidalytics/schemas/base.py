from dataclasses import dataclass

class SecondaryException(Exception):
    pass

class JSONDataClass:
    def __post_init__(self) -> None:
        # This class should be used as a base class for all dataclasses
        for key, value in self.__dict__.items():
            # This is a hack to get around the fact that there is a key in the
            # JSON that has a double underscore prefix. Since double underscore
            # triggers name mangling, we circumvent that by using a single
            # underscore prefix instead, and then replacing it with a double
            # underscore.
            if key[0] == "_":
                keyval = "_" + key
            else:
                keyval = key

            try:
                if isinstance(value, dict):
                    # Find the class that corresponds to the value of the key
                    # in the JSON. Wrap in try/except in case the specific class
                    # is a subclass.
                    annotations = self.get_annotations()
                    cls = annotations[keyval]
                    print(f"cls: {cls.__name__}, key: {keyval}")
                    setattr(self, keyval, cls(**value))
                elif (
                    isinstance(value, list)
                    and (len(value) > 0)
                    and isinstance(value[0], dict)
                ):
                    annotations = self.get_annotations()
                    super_cls = annotations[keyval]
                    cls = super_cls.__args__[0]
                    print(f"super_cls: {super_cls.__name__} cls: {cls.__name__}, key: {keyval}")
                    setattr(self, keyval, [cls(**item) for item in value])
            except Exception as e:
                if not isinstance(e, SecondaryException):
                    print(f"key: {keyval}, value: {value}")
                    raise SecondaryException from e
                else:
                    raise e
    
    @classmethod
    def get_annotations(cls) -> dict[str, type]:
        annotations = {}
        for c in cls.mro():
            try:
                annotations.update(**c.__annotations__)
            except AttributeError:
                pass
        return annotations