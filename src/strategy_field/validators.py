from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from .exceptions import StrategyNameError
from .utils import get_class

if TYPE_CHECKING:
    from .registry import Registry


@deconstructible
class ClassnameValidator(BaseValidator):
    message = _("Ensure this value is valid class name (it is %(show_value)s).")
    code = "classname"

    def __call__(self, value: Any) -> bool:
        cleaned = self.clean(value)
        params = {"show_value": cleaned, "value": value}
        try:
            get_class(cleaned)
        except (ImportError, TypeError, StrategyNameError):
            raise ValidationError(self.message, code=self.code, params=params) from None
        return True


@deconstructible
class RegistryValidator(ClassnameValidator):
    message = _("Invalid entry `%(show_value)s`")
    code = "registry"

    def __init__(self, registry: Registry, message: str | None = None) -> None:
        super().__init__(registry, message)
        self.registry = registry  # aliasing self.limit_value for readability

    def __call__(self, value: Any) -> bool:
        cleaned = self.clean(value)
        params = {"show_value": cleaned, "value": value}
        try:
            if isinstance(value, (list, tuple)):
                return all(issubclass(get_class(c), self.registry.klass) for c in cleaned)
            value = get_class(cleaned)
        except (ImportError, TypeError, StrategyNameError):
            raise ValidationError(self.message, code=self.code, params=params) from None

        if not issubclass(value, self.registry.klass):
            raise ValidationError(self.message, code=self.code, params=params) from None
        return True
