import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from strategy_field.forms import StrategyFormField
from strategy_field.utils import fqn


def test_formfield_wrong_classname(registry):
    f = StrategyFormField(registry=registry, choices=registry.as_choices())
    with pytest.raises(ValidationError):
        assert f.clean('wrong name')


def test_formfield_invalid_classname(registry):
    f = StrategyFormField(registry=registry, choices=registry.as_choices())
    with pytest.raises(ValidationError):
        assert f.clean(fqn(User))


def test_formfield_valid(registry):
    f = StrategyFormField(registry=registry, choices=registry.as_choices())
    # assert f.clean(fqn(registry[0]))
    assert f.clean('demoproject.demoapp.models.Sender1')


def test_formfield_empty(registry):
    f = StrategyFormField(registry=registry, choices=registry.as_choices())
    # assert f.clean(fqn(registry[0]))
    assert f.clean('demoproject.demoapp.models.Sender1')
