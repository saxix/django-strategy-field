# -*- coding: utf-8 -*-
import pytest

from demoproject.demoapp.models import (AbstractSender, DemoModel, Sender1,
                                        Sender2,)
from strategy_field.registry import Registry
from strategy_field.utils import fqn


def test_registry():
    r = Registry(AbstractSender)
    r.register(Sender1)

    assert Sender1 in r
    assert fqn(Sender1) in r
    assert Sender2 not in r


def test_registry_check_classes():
    r = Registry(AbstractSender)
    with pytest.raises(ValueError):
        r.register(DemoModel)


def test_registry_bypass_class_check():
    r = Registry(None)
    r.register(DemoModel)
    r.register(AbstractSender)
    r.register(Sender1)

    assert Sender1 in r
    assert AbstractSender in r
    assert DemoModel in r


def test_registry_string():
    r = Registry('demoproject.demoapp.models.AbstractSender')
    r.register(Sender1)

    assert Sender1 in r
    assert fqn(Sender1) in r
    assert Sender2 not in r
