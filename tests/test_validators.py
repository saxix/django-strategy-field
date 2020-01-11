import pytest
from django.core.exceptions import ValidationError

from strategy_field.validators import ClassnameValidator, RegistryValidator


def test_classnamevalidator():
    v = ClassnameValidator(None)
    assert v('strategy_field.validators.ClassnameValidator')
    with pytest.raises(ValidationError):
        v('error')



def test_RegistryValidator(registry):
    v = RegistryValidator(registry)
    assert v('demoproject.demoapp.models.Sender1')

    with pytest.raises(ValidationError):
        v('demoproject.demoapp.models.Strategy1')

    with pytest.raises(ValidationError):
        v('error')

    v(['demoproject.demoapp.models.Strategy1'])

    with pytest.raises(ValidationError):
        v(['error'])
