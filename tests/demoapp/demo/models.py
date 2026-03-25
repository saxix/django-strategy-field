import logging

from django.core.mail.backends.base import BaseEmailBackend
from django.db import models

from strategy_field.fields import (
    MultipleStrategyClassField,
    MultipleStrategyField,
    StrategyClassField,
    StrategyField,
)
from strategy_field.registry import Registry
from strategy_field.utils import fqn, import_by_name

logger = logging.getLogger(__name__)


class AbstractSender:
    def __str__(self):
        return "oooooo"


class Sender1(AbstractSender):
    pass


class Sender2(AbstractSender):
    pass


class SenderNotRegistered(AbstractSender):
    pass


class SenderWrong:
    pass


registry = Registry(AbstractSender)
registry.register(Sender1)
registry.register(Sender2)


class AbstractStrategy:
    def __init__(self, context, label=""):
        if not context:
            raise ValueError("Invalid context for strategy ({})".format(context))
        self.context = context
        self.label = label


class Strategy1(AbstractStrategy):
    label = "strategy"
    none = None

    @classmethod
    def verbose_name(cls):
        return "Verbose Name"

    def __str__(self):
        return "Verbose Strategy1"


class Strategy2(AbstractStrategy):
    def __str__(self):
        return "Verbose Strategy2"


class StrategyRegistry(Registry):
    def deserialize(self, value, obj=None):
        ret = []
        if isinstance(value, str):
            value = value.split(",")
        for v in value:
            klass = v
            if isinstance(klass, str):
                klass = import_by_name(klass)
            if not issubclass(klass, self.klass):
                raise ValueError(fqn(klass))
            ret.append(klass(obj))
        return ret


registry1 = StrategyRegistry(AbstractStrategy)
registry1.register(Strategy1)
registry1.register(Strategy2)


class DemoAllModel(models.Model):
    choice = StrategyClassField(registry=registry)
    multiple = MultipleStrategyClassField(registry=registry)
    custom = StrategyField(registry=registry1)
    custom_multiple = MultipleStrategyField(registry=registry1)

    def __str__(self):
        return f"{self.choice}"


class DemoModel(models.Model):
    sender = StrategyClassField(registry=registry)

    def __str__(self):
        return f"{self.sender}"


def aa():
    def cc(s):
        return registry

    return cc


class DemoCallableModel(models.Model):
    sender = StrategyClassField(registry=aa())

    def __str__(self):
        return f"{self.sender}"


class DemoModelNone(models.Model):
    sender = StrategyClassField(registry=registry, null=True, blank=True)

    def __str__(self):
        return f"{self.sender}"


class DemoModelDefault(models.Model):
    sender = StrategyClassField(null=True, registry=registry, default="demo.models.Sender1")

    def __str__(self):
        return f"{self.sender}"


def cc():
    return "demo.models.Sender1"


class DemoModelCallableDefault(models.Model):
    sender = StrategyClassField(registry=registry, null=True, default=cc)

    def __str__(self):
        return f"{self.sender}"


class DemoModelProxy(DemoModel):
    class Meta:
        proxy = True

    def __str__(self):
        return f"{self.sender}"


class DemoMultipleModel(models.Model):
    sender = MultipleStrategyClassField(registry=registry, null=True, blank=True)

    def __str__(self):
        return f"{self.sender}"


class DemoCustomModel(models.Model):
    sender = StrategyField(registry=registry1)

    def __str__(self):
        return f"{self.sender}"


class DemoMultipleCustomModel(models.Model):
    sender = MultipleStrategyField(registry=registry1)

    def __str__(self):
        return f"{self.sender}"


class DemoModelContext(models.Model):
    def __str__(self):
        return "demo"


# funny code. just for tests
def factory(klass, context):
    if issubclass(klass, BaseEmailBackend):
        return klass(file_path="")
    return klass()


class DemoModelNoRegistry(models.Model):
    klass = StrategyClassField(blank=True, null=True)
    instance = StrategyField(factory=factory, blank=True, null=True)

    def __str__(self):
        return f"{self.klass}"
