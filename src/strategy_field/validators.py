from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from .exceptions import StrategyNameError
from .utils import get_class


@deconstructible
class ClassnameValidator(BaseValidator):
    message = _("Ensure this value is valid class name (it is %(show_value)s).")
    code = "classname"

    def __call__(self, value):
        cleaned = self.clean(value)
        params = {"show_value": cleaned, "value": value}
        try:
            get_class(cleaned)
        except (ImportError, TypeError, StrategyNameError):
            raise ValidationError(self.message, code=self.code, params=params)
        return True


@deconstructible
class RegistryValidator(ClassnameValidator):
    message = _("Invalid entry `%(show_value)s`")
    code = "registry"

    def __init__(self, registry, message=None):
        super().__init__(registry, message)
        self.registry = registry  # aliasing self.limit_value for readability

    def __call__(self, value):
        cleaned = self.clean(value)
        params = {"show_value": cleaned, "value": value}
        try:
            if isinstance(value, (list, tuple)):
                for c in cleaned:
                    if not issubclass(get_class(c), self.registry.klass):
                        return False
                return True
            else:
                value = get_class(cleaned)
        except (ImportError, TypeError, StrategyNameError):
            raise ValidationError(self.message, code=self.code, params=params)

        if not issubclass(value, self.registry.klass):
            raise ValidationError(self.message, code=self.code, params=params)
        return True
