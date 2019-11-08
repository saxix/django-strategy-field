# -*- coding: utf-8 -*-
import importlib
import logging
from inspect import isclass
import types

logger = logging.getLogger(__name__)


class ModulesCache(dict):
    def __missing__(self, name):
        if '.' not in name:
            raise ValueError("Cannot import '{}'".format(name))

        module_path, class_str = name.rsplit(".", 1)
        module = importlib.import_module(module_path)
        try:
            handler = getattr(module, class_str)
            self[name] = handler
            return handler
        except AttributeError:
            raise AttributeError('Unable to import {}. '
                                 '{} does not have {} attribute'.format(name,
                                                                        module,
                                                                        class_str))


_cache = ModulesCache()


def get_class(value):
    if not value:
        return value
    elif isinstance(value, str):
        return import_by_name(value)
    elif isclass(value):
        return value
    else:
        return type(value)


def get_display_string(klass, display_attribute=None):
    if display_attribute and hasattr(klass, display_attribute):
        attr = getattr(klass, display_attribute)
        if attr is None:
            return fqn(klass)
        elif callable(attr):
            return attr()
        else:
            return attr

    return fqn(klass)


def get_attr(obj, attr, default=None):
    """Recursive get object's attribute. May use dot notation.

    """
    if '.' not in attr:
        return getattr(obj, attr, default)
    else:
        L = attr.split('.')
        return get_attr(getattr(obj, L[0], default), '.'.join(L[1:]), default)


def fqn(o):
    """Returns the fully qualified class name of an object or a class

    :param o: object or class
    :return: class name
    """
    parts = []
    if isinstance(o, str):
        return o
    if not hasattr(o, '__module__'):
        raise ValueError('Invalid argument `%s`' % o)
    parts.append(o.__module__)
    if isclass(o):
        parts.append(o.__name__)
    elif isinstance(o, types.FunctionType):
        parts.append(o.__name__)
    else:
        parts.append(o.__class__.__name__)
    return ".".join(parts)


def import_by_name(name):
    """dynamically load a class from a string

    es:
        klass = import_by_name('my_package.my_module.my_class')
        some_object = klass()

    :param name:
    :return:

    """
    return _cache[name]

    # if '.' not in name:
    #     raise ValueError("Cannot import '{}'".format(name))
    # class_data = name.split(".")
    # module_path = ".".join(class_data[:-1])
    # class_str = class_data[-1]
    # module = importlib.import_module(module_path)
    # try:
    #     return getattr(module, class_str)
    # except AttributeError:
    #     raise AttributeError('Unable to import {}. '
    #                          '{} does not have {} attribute'.format(name,
    #                                                                 module,
    #                                                                 class_str))


def stringify(value):
    ret = []
    # if isinstance(value, six.string_types):
    #     value = value.split(',')
    for v in value:
        if isinstance(v, str) and v:
            ret.append(v)
        else:
            ret.append(fqn(v))
    return ",".join(sorted(ret))
