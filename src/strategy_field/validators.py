from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from strategy_field.utils import get_class


@deconstructible
class ClassnameValidator2(BaseValidator):
    message = _('Ensure this value is valid class name (it is %(show_value)s).')
    code = 'classname'

    #
    # def __init__(self, resolver, message=None):
    #     super().__init__(resolver, message)
    #     self.resolver = resolver # aliasing self.limit_value for readability

    def compare(self, a, b):
        try:
            self.resolver.get_class(a)
        except (ImportError, TypeError):
            return True
        return False


@deconstructible
class ClassnameValidator(BaseValidator):
    message = _('Ensure this value is valid class name (it is %(show_value)s).')
    code = 'classname'

    def __call__(self, value):
        cleaned = self.clean(value)
        # limit_value = self.limit_value() if callable(self.limit_value) else self.limit_value
        params = {'limit_value': "-", 'show_value': cleaned, 'value': value}
        try:
            get_class(cleaned)
        except (ImportError, TypeError):
            raise ValidationError(self.message, code=self.code, params=params)


@deconstructible
class RegistryValidator(ClassnameValidator):
    # message = _('Ensure this value is registered (it is %(show_value)s).')
    message = _('Invalid entry `%(show_value)s`')
    code = 'registry'

    def __init__(self, registry, message=None):
        super().__init__(registry, message)
        self.registry = registry  # aliasing self.limit_value for readability

    def __call__(self, value):
        cleaned = self.clean(value)
        # limit_value = self.limit_value() if callable(self.limit_value) else self.limit_value
        params = {'limit_value': "-", 'show_value': cleaned, 'value': value}
        try:
            if isinstance(value, (list, tuple)):
                for c in cleaned:
                    if not issubclass(get_class(c), self.registry.klass):
                        return False
                return True
            else:
                value = get_class(cleaned)
        except (ImportError, TypeError):
            raise ValidationError(self.message, code=self.code, params=params)

        if not issubclass(value, self.registry.klass):
            raise ValidationError(self.message, code=self.code, params=params)
