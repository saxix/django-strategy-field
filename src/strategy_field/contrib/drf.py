# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from rest_framework import serializers

from strategy_field.fields import ClassnameValidator
from strategy_field.utils import import_by_name, fqn

logger = logging.getLogger(__name__)


class DrfStrategyField(serializers.ChoiceField):
    default_validators = [ClassnameValidator]

    def __init__(self, registry, **kwargs):
        choices = registry.as_choices()
        super(DrfStrategyField, self).__init__(choices, **kwargs)
        self.registry = registry

    def to_representation(self, obj):
        return fqn(obj)

    def to_internal_value(self, data):
        return data


class DrfMultipleStrategyField(serializers.ChoiceField):
    default_validators = [ClassnameValidator]

    def __init__(self, registry, **kwargs):
        choices = registry.as_choices()
        super(DrfMultipleStrategyField, self).__init__(choices, **kwargs)
        self.registry = registry

    def to_representation(self, obj):
        return [fqn(i) for i in obj]

    def to_internal_value(self, data):
        return [import_by_name(i) for i in data]

    def run_validators(self, value):
        return super(DrfMultipleStrategyField, self).run_validators(value)
