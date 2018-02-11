# -*- coding: utf-8 -*-
import logging

import six
from django.core.mail.backends.base import BaseEmailBackend

from django.db import models
from django.utils.deconstruct import deconstructible

from strategy_field.fields import (MultipleStrategyClassField,
                                   MultipleStrategyField, StrategyClassField,
                                   StrategyField)
from strategy_field.registry import Registry
from strategy_field.utils import fqn, import_by_name

logger = logging.getLogger(__name__)


class AbstractSender(object):
    pass


class Sender1(AbstractSender):
    pass


class Sender2(AbstractSender):
    pass


class SenderNotRegistered(AbstractSender):
    pass


class SenderWrong(object):
    pass


registry = Registry(AbstractSender)
registry.register(Sender1)
registry.register(Sender2)


class AbstractStrategy(object):
    def __init__(self, context, label=''):
        if not context:
            raise ValueError("Invalid context for strategy ('')".format(context))
        self.context = context
        self.label = label


class Strategy(AbstractStrategy):
    label = 'strategy'
    
    @classmethod
    def verbose_name(self):
        return "Verbose Name"
    


class Strategy1(AbstractStrategy):
    pass


class StrategyRegistry(Registry):
    def deserialize(self, value, obj=None):
        ret = []
        if isinstance(value, six.string_types):
            value = value.split(',')
        for v in value:
            if isinstance(v, six.string_types):
                v = import_by_name(v)
            if not issubclass(v, self.klass):
                raise ValueError(fqn(v))
            ret.append(v(obj))
        return ret


registry1 = StrategyRegistry(AbstractStrategy)
registry1.register(Strategy)
registry1.register(Strategy1)


class DemoAllModel(models.Model):
    choice = StrategyClassField(registry=registry)
    multiple = MultipleStrategyClassField(registry=registry)
    custom = StrategyField(registry=registry1)
    custom_multiple = MultipleStrategyField(registry=registry1)


class DemoModel(models.Model):
    sender = StrategyClassField(registry=registry)


def aa():
    def cc(s):
        return registry

    return cc


class DemoCallableModel(models.Model):
    sender = StrategyClassField(registry=aa())


class DemoModelNone(models.Model):
    sender = StrategyClassField(registry=registry, null=True, blank=True)


class DemoModelDefault(models.Model):
    sender = StrategyClassField(null=True,
                                registry=registry,
                                default='demoproject.demoapp.models.Sender1')


def cc():
    return 'demoproject.demoapp.models.Sender1'


class DemoModelCallableDefault(models.Model):
    sender = StrategyClassField(registry=registry, null=True,
                                default=cc
                                )


class DemoModelProxy(DemoModel):
    class Meta:
        proxy = True


class DemoMultipleModel(models.Model):
    sender = MultipleStrategyClassField(registry=registry, null=True, blank=True)


class DemoCustomModel(models.Model):
    sender = StrategyField(registry=registry1)


class DemoMultipleCustomModel(models.Model):
    sender = MultipleStrategyField(registry=registry1)


class DemoModelContext(models.Model):
    pass


# funny code. just for tests
def factory(klass, context):
    if issubclass(klass, BaseEmailBackend):
        return klass(file_path='')
    return klass()


class DemoModelNoRegistry(models.Model):
    klass = StrategyClassField(blank=True, null=True)
    instance = StrategyField(factory=factory, blank=True, null=True)
