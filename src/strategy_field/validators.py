from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class ClassnameValidator(BaseValidator):
    message = _('Ensure this value is valid class name (it is %(show_value)s).')
    code = 'classname'

    def __init__(self, resolver, message=None):
        super().__init__(resolver, message)
        self.resolver = resolver # aliasing self.limit_value for readability

    def compare(self, a, b):
        try:
            self.resolver.get_class(a)
        except (ImportError, TypeError):
            return True
        return False


@deconstructible
class RegistryValidator(ClassnameValidator):
    # message = _('Ensure this value is registered (it is %(show_value)s).')
    message = _('Invalid entry `%(show_value)s`')
    code = 'registry'

    def __init__(self, registry, message=None):
        super().__init__(registry, message)
        self.registry = registry # aliasing self.limit_value for readability

    def compare(self, value, registry):
        if value is None:
            return False
        elif isinstance(value, (list, tuple)):
            for c in value:
                if not issubclass(self.registry.resolver.get_class(value), registry.klass):
                    return False
        else:
            value = self.registry.resolver.get_class(value)
        return not issubclass(value, registry.klass)

