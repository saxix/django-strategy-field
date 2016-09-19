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

    def is_valid(self, value):
        if value and isinstance(value, six.string_types):
            value = import_by_name(value)

        if self.klass:
            return (isclass(value) and issubclass(value, self.klass)) or \
                   (isinstance(value, self.klass))

        return True

    def as_choices(self):
        if not self._choices:
            self._choices = sorted((fqn(klass), fqn(klass)) for klass in self)
        return self._choices

    def append(self, x):
        if isinstance(x, six.string_types):
            x = import_by_name(x)

        if self.klass and not issubclass(x, self.klass):
            raise ValueError("%s is not a subtype of %s" % (x, self.klass))

        if get_attr(x, 'Meta.abstract'):
            raise ValueError

        super(Registry, self).append(x)
        self._choices = None

    register = append

    def __contains__(self, y):
        if isinstance(y, six.string_types):
            try:
                y = import_by_name(y)
            except (ImportError, ValueError):
                return False
        return super(Registry, self).__contains__(y)
