# -*- coding: utf-8 -*-
import logging

import six

from django.db import models
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

    def __init__(self, context):
        self.context = context


class Strategy(AbstractStrategy):
    pass


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


class DemoModelNone(models.Model):
    sender = StrategyClassField(registry=registry, null=True, blank=True)


class DemoModelDefault(models.Model):
    sender = StrategyClassField(null=True,
                                registry=registry,
                                default='demoproject.demoapp.models.Sender1')


class DemoModelCallableDefault(models.Model):
    sender = StrategyClassField(registry=registry, null=True,
                                default=lambda: 'demoproject.demoapp.models.Sender1')


class DemoModelProxy(DemoModel):

    class Meta:
        proxy = True


class DemoMultipleModel(models.Model):
    sender = MultipleStrategyClassField(registry=registry)


class DemoCustomModel(models.Model):
    sender = StrategyField(registry=registry1)


class DemoMultipleCustomModel(models.Model):
    sender = MultipleStrategyField(registry=registry1)


class DemoModelContext(models.Model):
    pass


# class DemoModelGetter(models.Model):
    # fk = models.ForeignKey(DemoModelContext)
    # sender = StrategyField(registry=registry1, getter=lambda s: s.fk)
