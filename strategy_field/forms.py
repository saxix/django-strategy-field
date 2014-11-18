# -*- coding: utf-8 -*-
import six
from django.forms.fields import TypedChoiceField, TypedMultipleChoiceField
from .utils import fqn
from strategy_field.utils import stringify


class StrategyFormField(TypedChoiceField):
    def __init__(self, *args, **kwargs):
        self.registry = kwargs.pop('registry')
        super(StrategyFormField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        if isinstance(value, six.string_types):
            return value
        if value:
            return fqn(value)
        return value


class StrategyMultipleChoiceFormField(TypedMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        self.registry = kwargs.pop('registry')
        super(StrategyMultipleChoiceFormField, self).__init__(*args, **kwargs)

    # def _get_choices(self):
    #     return super(StrategyMultipleChoiceFormField, self)._get_choices()

    def prepare_value(self, value):
        ret = value
        if isinstance(value, six.string_types):
            ret = [value]
        elif isinstance(value, (list, tuple)):
            ret = stringify(value)
        if ret:
            return ret.split(',')

    def valid_value(self, value):
        return value in self.registry
