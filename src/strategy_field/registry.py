# -*- coding: utf-8 -*-
import logging
import six
from inspect import isclass

from django.utils.functional import cached_property

from .utils import fqn, get_attr, import_by_name, get_display_string  # noqa

logger = logging.getLogger(__name__)


class Registry(list):
    klass = None

    def __init__(self, *args):
        self._klass = args[0]
        self._choices = None
        list.__init__(self, *args[1:])

    @cached_property
    def klass(self):
        if isinstance(self._klass, six.string_types):
            return import_by_name(self._klass)
        return self._klass

    def get_name(self, entry):
        return str(entry)

    def is_valid(self, value):
        if value and isinstance(value, six.string_types):
            try:
                value = import_by_name(value)
            except (ImportError, ValueError, AttributeError):
                return False

        if self.klass:
            return (isclass(value) and issubclass(value, self.klass)) or \
                   (isinstance(value, self.klass))

        return True

    def as_choices(self):
        if not self._choices:
            self._choices = sorted((fqn(klass), fqn(klass)) for klass in self)
        return self._choices

    def append(self, class_or_fqn):
        if isinstance(class_or_fqn, six.string_types):
            cls = import_by_name(class_or_fqn)
        else:
            cls = class_or_fqn

        if cls == self.klass:
            return

        if self.klass and not issubclass(cls, self.klass):
            raise ValueError("'%s' is not a subtype of %s" % (class_or_fqn, self.klass))

        super(Registry, self).append(cls)
        self._choices = None
        return class_or_fqn

    register = append

    def __contains__(self, y):
        if isinstance(y, six.string_types):
            try:
                y = import_by_name(y)
            except (ImportError, ValueError):
                return False
        return super(Registry, self).__contains__(y)
