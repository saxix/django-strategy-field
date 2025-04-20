from decimal import Decimal

import pytest
from demo.models import AbstractSender, DemoModel, Sender1, Sender2, SenderNotRegistered

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
    assert DemoModel() in r
    assert 22 not in r


def test_registry_string():
    r = Registry("demo.models.AbstractSender")
    r.register(Sender1)

    assert Sender1 in r
    assert fqn(Sender1) in r
    assert Sender2 not in r


def test_registry_is_valid():
    r = Registry("demo.models.AbstractSender")

    assert r.is_valid(Sender1)
    assert r.is_valid(fqn(Sender1))
    assert not r.is_valid(DemoModel)

    r = Registry(None)
    assert r.is_valid(Sender1)
    assert r.is_valid(DemoModel)
    assert not r.is_valid("demo.models.Wrong")


def test_registry_append():
    r = Registry("demo.models.AbstractSender")

    assert r.register(Sender1)
    assert r.register(fqn(Sender2))
    assert not r.register("demo.models.AbstractSender")


def test_registry_as_choices(monkeypatch):
    r = Registry("demo.models.AbstractSender", label_attribute="label")

    r.register(Sender1)
    r.register(Sender2)
    r.register(fqn(Sender1))
    monkeypatch.setattr(Sender1, "label", classmethod(lambda s: "LABEL"), raising=False)

    assert r.as_choices() == [
        ("demo.models.Sender1", "LABEL"),
        ("demo.models.Sender2", "demo.models.Sender2"),
    ]


@pytest.mark.parametrize("entry", [Sender1, fqn(Sender1), Sender1()])
def test_registry_contains(entry):
    r = Registry(AbstractSender)
    r.register(Sender1)
    r.register(fqn(Sender2))
    assert entry in r


@pytest.mark.parametrize(
    "entry",
    [
        SenderNotRegistered,
        fqn(SenderNotRegistered),
        SenderNotRegistered(),
        None,
        "a.b.c",
        100,
        Decimal(10),
        1.1,
        b"bytes",
    ],
)
def test_registry_not_contains(entry):
    r = Registry(AbstractSender)
    assert entry not in r
