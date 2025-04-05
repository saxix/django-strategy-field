from __future__ import annotations

import logging
from inspect import isclass
from typing import Any

from django.utils.functional import cached_property

from .utils import fqn, get_class, get_display_string, import_by_name

logger = logging.getLogger(__name__)


class Registry(list):
    def __init__(self, base_class: type, *args: Any, **kwargs: Any) -> None:
        self._klass = base_class
        self._label_attribute = kwargs.get("label_attribute")
        self._choices = None
        list.__init__(self, *args[:])

    @cached_property
    def klass(self) -> Any:
        if isinstance(self._klass, str):
            return import_by_name(self._klass)
        return self._klass

    def get_name(self, entry: type) -> str:
        return get_display_string(entry, self._label_attribute)

    def get_by_name(self, entry: str) -> Any:
        return get_class(entry)

    def is_valid(self, value: str) -> bool:
        if value and isinstance(value, str):
            try:
                value = import_by_name(value)
            except (ImportError, ValueError, AttributeError):
                return False

        if self.klass:
            return (isclass(value) and issubclass(value, self.klass)) or (isinstance(value, self.klass))

        return True

    def as_choices(self) -> tuple[str, str]:
        if not self._choices:
            self._choices = sorted((fqn(klass), self.get_name(klass)) for klass in self)
        return self._choices

    def register(self, class_or_fqn: type | str) -> Any:
        cls = import_by_name(class_or_fqn) if isinstance(class_or_fqn, str) else class_or_fqn

        if cls == self.klass:
            return None

        if self.klass and not issubclass(cls, self.klass):
            raise ValueError(f"'{class_or_fqn}' is not a subtype of {self.klass}")

        if cls in self:
            return None

        super().append(cls)
        self._choices = None
        return class_or_fqn

    def append(self, class_or_fqn: type | str) -> None:
        self.register(class_or_fqn)

    def __contains__(self, y: Any) -> bool:
        if isinstance(y, str):
            try:
                return super().__contains__(import_by_name(y))
            except (ImportError, ValueError):
                return False
        elif isclass(y):
            return super().__contains__(y)
        elif (self._klass and isinstance(y, self._klass)) or isinstance(y, object):
            return super().__contains__(type(y))
        return super().__contains__(y)
