# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.forms.fields import ChoiceField, TypedMultipleChoiceField

from strategy_field.utils import fqn, stringify


class StrategyFormField(ChoiceField):
    def __init__(self, *args, **kwargs):
        self.display_attribute = kwargs.pop('display_attribute', None)
        self.registry = kwargs.pop('registry')
        self.empty_value = kwargs.pop('empty_value', '')
        super(StrategyFormField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        if isinstance(value, str):
            return value
        if value:
            return fqn(value)

    def bound_data(self, data, initial):
        if isinstance(data, str):
            return data
        return fqn(data)

    def valid_value(self, value):
        return value in self.registry

    def _coerce(self, value):
        if value == self.empty_value or value in self.empty_values:
            return self.empty_value
        try:
            v = self.to_python(value)
            if v in self.registry:
                return v
            else:
                raise ValidationError
        except (ValueError, TypeError, ValidationError):
            raise ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': value},
            )

    def clean(self, value):
        value = super(StrategyFormField, self).clean(value)
        return self._coerce(value)


class StrategyMultipleChoiceFormField(TypedMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        self.registry = kwargs.pop('registry')
        self.display_attribute = kwargs.pop('display_attribute', None)

        super(StrategyMultipleChoiceFormField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        ret = value
        if isinstance(value, str):
            ret = [value]
        if isinstance(value, (list, tuple)):
            ret = stringify(value)
        if ret:
            return ret.split(',')

    def valid_value(self, value):
        return value in self.registry
