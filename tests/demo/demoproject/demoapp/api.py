# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from demoproject.demoapp.models import DemoMultipleModel, DemoModel
from strategy_field.utils import fqn, stringify

logger = logging.getLogger(__name__)


class StrategyClassFieldDrf(serializers.CharField):
    def to_representation(self, value):
        return fqn(value)


class MultipleStrategyClassFieldDrf(serializers.CharField):
    def to_representation(self, value):
        return stringify(value)


class DemoModelSerializer(serializers.ModelSerializer):
    sender = StrategyClassFieldDrf()

    class Meta:
        model = DemoModel


class DemoMultipleModelSerializer(serializers.ModelSerializer):
    sender = MultipleStrategyClassFieldDrf()

    class Meta:
        model = DemoMultipleModel


class DemoModelView(ModelViewSet):
    serializer_class = DemoModelSerializer
    queryset = DemoModel.objects.all()


class DemoMultipleModelView(ModelViewSet):
    serializer_class = DemoMultipleModelSerializer
    queryset = DemoMultipleModel.objects.all()
