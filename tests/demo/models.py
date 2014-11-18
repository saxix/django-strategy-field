# -*- coding: utf-8 -*-
import logging
import six
from django.db import models
from strategy_field.fields import MultipleStrategyClassField, StrategyClassField, StrategyField, MultipleStrategyField
from strategy_field.registry import Registry
# from .fields import CustomStrategyField, CustomMultipleStrategyField
from strategy_field.utils import import_by_name, fqn

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
    choice = StrategyClassField(registry)
    multiple = MultipleStrategyClassField(registry)
    custom = StrategyField(registry)
    custom_multiple = MultipleStrategyField(registry)


class DemoModel(models.Model):
    sender = StrategyClassField(registry)


class DemoModelNone(models.Model):
    sender = StrategyClassField(registry, null=True, blank=True)


class DemoModelDefault(models.Model):
    sender = StrategyClassField(registry, default=lambda: registry[0])


class DemoModelProxy(DemoModel):
    class Meta:
        proxy = True


class DemoMultipleModel(models.Model):
    sender = MultipleStrategyClassField(registry)


class DemoCustomModel(models.Model):
    sender = StrategyField(registry=registry1)


class DemoMultipleCustomModel(models.Model):
    sender = MultipleStrategyField(registry=registry1)
