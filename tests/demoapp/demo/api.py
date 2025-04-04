import logging

from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from demo.models import DemoModelNone, DemoMultipleModel, registry
from strategy_field.contrib.drf import DrfMultipleStrategyField, DrfStrategyField

logger = logging.getLogger(__name__)


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
