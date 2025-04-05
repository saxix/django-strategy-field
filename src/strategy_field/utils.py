from __future__ import annotations

import importlib
import logging
import types
from inspect import isclass
from typing import Any, Sequence

from django.utils.module_loading import import_string

from . import config
from .exceptions import StrategyAttributeError, StrategyClassError, StrategyNameError

logger = logging.getLogger(__name__)


class ModulesCache(dict):
    def __missing__(self, name: str) -> Any:
        if "." not in name:
            raise StrategyNameError(name)

        module_path, class_str = name.rsplit(".", 1)
        module = importlib.import_module(module_path)
        try:
            handler = getattr(module, class_str)
            self[name] = handler
            return handler
        except AttributeError:
            raise StrategyAttributeError(name, module_path, class_str) from None


_cache = ModulesCache()


def default_classloader(value: str | type | None) -> Any:
    if not value:
        return None
    if isinstance(value, str):
        return import_by_name(value)
    if isclass(value):
        return value

    t = type(value)
    if t.__module__ in ("builtins", "__builtin__"):
        return None
    return t


importer = None


def get_class(value: str) -> Any:
    global importer  # noqa: PLW0603
    if importer is None:
        importer = import_string(config.CLASSLOADER)
    return importer(value)


def get_display_string(klass: type, display_attribute: str | None = None) -> str:
    if display_attribute and hasattr(klass, display_attribute):
        attr = getattr(klass, display_attribute)
        if attr is None:
            return fqn(klass)
        if callable(attr):
            return str(attr())
        return str(attr)

    return fqn(klass)


def get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """Recursive get object's attribute. May use dot notation."""
    if "." not in attr:
        return getattr(obj, attr, default)
    parts = attr.split(".")
    return get_attr(getattr(obj, parts[0], default), ".".join(parts[1:]), default)


def fqn(o: Any) -> str:
    """Returns the fully qualified class name of an object or a class

    :param o: object or class
    :return: class name
    """
    parts = []
    if isinstance(o, str):
        return o
    if not hasattr(o, "__module__"):
        raise StrategyClassError(o)
    parts.append(o.__module__)
    if isclass(o) or isinstance(o, types.FunctionType):
        parts.append(o.__name__)
    else:
        parts.append(o.__class__.__name__)
    return ".".join(parts)


def import_by_name(name: str) -> Any:
    """dynamically load a class from a string

    es:
        klass = import_by_name('my_package.my_module.my_class')
        some_object = klass()

    :param name:
    :return:

    """
    return _cache[name]


def stringify(value: Sequence[Any]) -> str:
    ret = []
    for v in value:
        if isinstance(v, str) and v:
            ret.append(v)
        else:
            ret.append(fqn(v))
    return ",".join(sorted(ret))
