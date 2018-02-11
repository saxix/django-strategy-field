# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import six
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from demoproject.demoapp.models import DemoMultipleModel, DemoModel, DemoModelNone, registry
from strategy_field.contrib.drf import DrfStrategyField, DrfMultipleStrategyField
from strategy_field.utils import fqn, stringify

logger = logging.getLogger(__name__)


# class StrategyClassFieldDrf(serializers.CharField):
#     def to_representation(self, value):
#         return fqn(value)


# class MultipleStrategyClassFieldDrf(serializers.CharField):
#     def to_representation(self, value):
#         return stringify(value)


class DemoModelSerializer(serializers.ModelSerializer):
    sender = DrfStrategyField(registry, required=False)

    class Meta:
        model = DemoModelNone
        exclude = []


class DemoMultipleModelSerializer(serializers.ModelSerializer):
    sender = DrfMultipleStrategyField(registry)

    class Meta:
        model = DemoMultipleModel
        exclude = []


class DemoModelView(ModelViewSet):
    serializer_class = DemoModelSerializer
    queryset = DemoModelNone.objects.all()


class DemoMultipleModelView(ModelViewSet):
    serializer_class = DemoMultipleModelSerializer
    queryset = DemoMultipleModel.objects.all()
