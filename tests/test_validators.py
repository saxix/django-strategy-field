from contextlib import nullcontext as does_not_raise

import pytest
from django.core.exceptions import ValidationError

from strategy_field.validators import ClassnameValidator, RegistryValidator


def test_classnamevalidator():
    v = ClassnameValidator(None)
    with does_not_raise():
        v("strategy_field.validators.ClassnameValidator")
    with pytest.raises(ValidationError):
        v("error")


def test_registryvalidator(registry):
    v = RegistryValidator(registry)
    with does_not_raise():
        v("demo.models.Sender1")

    with pytest.raises(ValidationError):
        v("demo.models.Strategy1")

    with pytest.raises(ValidationError):
        v("error")

    with pytest.raises(ValidationError):
        v(["demo.models.Strategy1"])

    with pytest.raises(ValidationError):
        v(["error1", "error2"])
