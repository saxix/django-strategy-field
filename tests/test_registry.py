# -*- coding: utf-8 -*-
from fixtures import *  # noqa
import logging
import pytest
from strategy_field.registry import Registry
from demo.models import AbstractSender, Sender1, Sender2, DemoModel
from strategy_field.utils import fqn

logger = logging.getLogger(__name__)


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



