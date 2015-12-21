# -*- coding: utf-8 -*-
import six
import logging
from .utils import import_by_name, fqn, get_attr  # noqa

logger = logging.getLogger(__name__)


class Registry(list):
    klass = None

    def __init__(self, *args):
        self.klass = args[0]
        list.__init__(self, *args[1:])

    def as_choices(self):
        return sorted((fqn(i), fqn(i)) for i in self if i)

    def append(self, x):
        # if isinstance(x, six.string_types):
        #     x = import_by_name(x)

        if not issubclass(x, self.klass):
            raise ValueError("%s is not a subtype of %s" % (x, self.klass))

        if get_attr(x, 'Meta.abstract'):
            raise ValueError

        super(Registry, self).append(x)

    register = append

    def __contains__(self, y):
        if isinstance(y, six.string_types):
            try:
                y = import_by_name(y)
            except (ImportError, ValueError):
                return False
        return super(Registry, self).__contains__(y)
