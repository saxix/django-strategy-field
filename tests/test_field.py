from contextlib import nullcontext as does_not_raise
from unittest.mock import Mock

import pytest
from demo.models import DemoModelNoRegistry, Strategy1, registry1
from django.core.exceptions import ValidationError
from django.core.mail.backends.dummy import EmailBackend

from strategy_field.fields import MultipleStrategyClassField, MultipleStrategyField, StrategyClassField, StrategyField
from strategy_field.registry import Registry
from strategy_field.utils import fqn


class Dummy:
    pass


@pytest.mark.django_db
def test_no_registry_assign_class():
    d = DemoModelNoRegistry(klass=Dummy)
    d.save()
    assert d.klass == Dummy


@pytest.mark.django_db
def test_no_registry_assign_instance():
    d = DemoModelNoRegistry(instance=Dummy)
    d.save()
    assert isinstance(d.instance, Dummy)


@pytest.mark.django_db
def test_no_registry_assign_string():
    d = DemoModelNoRegistry(instance="django.core.mail.backends.dummy.EmailBackend")
    d.save()
    assert isinstance(d.instance, EmailBackend)


@pytest.mark.django_db
def test_wrong_strategy():
    d = DemoModelNoRegistry(instance="wrong.strategy")
    d.save()
    assert d.instance is None


@pytest.mark.django_db
def test_wrong_type():
    d = DemoModelNoRegistry(instance=1)
    d.save()
    assert d.instance is None


@pytest.mark.parametrize("cls", [StrategyClassField, StrategyField])
@pytest.mark.parametrize("kwargs", [{}, {"registry": Registry(None)}, {"choices": []}])
def test_deconstruct(cls, kwargs):
    f = cls(**kwargs)
    assert f.deconstruct() == (None, fqn(cls), [], {})


@pytest.mark.parametrize("cls", [StrategyClassField, StrategyField, MultipleStrategyClassField, MultipleStrategyField])
@pytest.mark.parametrize(
    ("value", "expectation"),
    [
        (Strategy1, does_not_raise()),
        (Strategy1(Mock()), does_not_raise()),
        ("a.b.c", pytest.raises(ValidationError)),
    ],
)
def test_validate(cls, value, expectation):
    f = cls(registry=registry1)
    with expectation:
        f.validate(value, Mock())
