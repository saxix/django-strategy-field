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


def test_registry_does_not_accept_wrong_classes():
    r = Registry(AbstractSender)
    with pytest.raises(ValueError):
        r.register(DemoModel)
