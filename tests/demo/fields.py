# -*- coding: utf-8 -*-
import logging
from inspect import isclass
import six
from strategy_field.fields import (StrategyClassFieldDescriptor, StrategyClassField,
                                   MultipleStrategyClassField, MultipleStrategyClassFieldDescriptor)
from strategy_field.utils import import_by_name

logger = logging.getLogger(__name__)


# class CustomStrategyFieldDescriptor(StrategyFieldDescriptor):
#     def __get__(self, obj, type=None):
#         if obj is None:
#             raise AttributeError('Can only be accessed via an instance.')
#         value = obj.__dict__.get(self.field.name)
#
#         if isinstance(value, self.field.registry.klass):
#             return value
#         elif isclass(value) and issubclass(value, self.field.registry.klass):
#             return value(obj)
#         elif isinstance(value, six.string_types):
#             return import_by_name(value)(obj)
#         elif value is None:
#             return None
#         raise ValueError(value)


# class CustomStrategyField(StrategyField):
#     descriptor = CustomStrategyFieldDescriptor


# class CustomMultipleStrategyFieldDescriptor(MultipleStrategyFieldDescriptor):
#     def __get__(self, obj, type=None):
#         if obj is None:
#             raise AttributeError('Can only be accessed via an instance.')
#         value = obj.__dict__.get(self.field.name)
#         if isinstance(value, six.string_types) or isinstance(value, (list, tuple)):
#             ret = []
#             if isinstance(value, six.string_types):
#                 value = value.split(',')
#             for v in value:
#                 if isinstance(v, six.string_types):
#                     v = import_by_name(v)
#
#                 if isclass(v) and not issubclass(v, self.field.registry.klass):
#                     raise ValueError(v)
#
#                 if isinstance(v, self.field.registry.klass):
#                     ret.append(v)
#                 else:
#                     ret.append(v(obj))
#
#             return ret
#         raise ValueError(value)
#
#     def __set__(self, obj, value):
#         obj.__dict__[self.field.name] = value


# class CustomMultipleStrategyField(MultipleStrategyField):
#     descriptor = CustomMultipleStrategyFieldDescriptor

