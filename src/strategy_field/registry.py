from __future__ import annotations

import logging
from inspect import isclass

from django.utils.functional import cached_property

from .utils import fqn, get_attr, get_class, get_display_string, import_by_name, importer  # noqa

logger = logging.getLogger(__name__)


class Registry(list):
    def __init__(self, base_class, *args, **kwargs):
        self._klass = base_class
        self._label_attribute = kwargs.get("label_attribute", None)
        self._choices = None
        list.__init__(self, *args[:])

    @cached_property
    def klass(self):
        if isinstance(self._klass, str):
            return import_by_name(self._klass)
        return self._klass

    def get_name(self, entry):
        return get_display_string(entry, self._label_attribute)

    def get_by_name(self, entry):
        return get_class(entry)

    def is_valid(self, value):
        if value and isinstance(value, str):
            try:
                value = import_by_name(value)
            except (ImportError, ValueError, AttributeError):
                return False

        if self.klass:
            return (isclass(value) and issubclass(value, self.klass)) or (isinstance(value, self.klass))

        return True

    def as_choices(self):
        if not self._choices:
            self._choices = sorted((fqn(klass), self.get_name(klass)) for klass in self)
        return self._choices

    def append(self, class_or_fqn) -> str | type | None:
        if isinstance(class_or_fqn, str):
            cls = import_by_name(class_or_fqn)
        else:
            cls = class_or_fqn

        if cls == self.klass:
            return None

        if self.klass and not issubclass(cls, self.klass):
            raise ValueError(f"'{class_or_fqn}' is not a subtype of {self.klass}")

        if cls in self:
            return None

        super().append(cls)
        self._choices = None
        return class_or_fqn

    register = append

    def __contains__(self, y):
        if isinstance(y, str):
            try:
                y = import_by_name(y)
            except (ImportError, ValueError):
                return False
        return super().__contains__(y)
