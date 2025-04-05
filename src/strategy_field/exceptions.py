from __future__ import annotations


class StrategyNameError(ValueError):
    default_message = "Invalid value '%s': must be a valid python dotted name."

    def __init__(self, name: str, message: str | None = None) -> None:
        self.name = str(name)
        self.message = message or self.default_message

    def __repr__(self) -> str:
        return self.message % self.name


class StrategyClassError(ValueError):
    default_message = "Invalid argument: '%s' is a invalid python name"

    def __init__(self, name: str, message: str | None = None) -> None:
        self.name = str(name)
        self.message = message or self.default_message

    def __repr__(self) -> str:
        return self.message % self.name


class StrategyImportError(ImportError):
    pass


class StrategyAttributeError(AttributeError):
    default_message = "Unable to import %(name)s. %(module)s does not have %(class_str)s attribute"

    def __init__(self, name: str, module_path: str, class_str: str, message: str | None = None) -> None:
        self.name = str(name)
        self.module_path = module_path
        self.class_str = class_str
        self.message = message or self.default_message

    def __repr__(self) -> str:
        return self.message % (self.name, self.module_path, self.class_str)
