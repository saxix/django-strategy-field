# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import pytest
from django_dynamic_fixture import G
from rest_framework.serializers import reverse

from demoproject.demoapp.models import (DemoModel, DemoMultipleModel, Sender1,
                                        Sender2,)
from strategy_field.utils import fqn, stringify

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_get_single(webapp):
    x = G(DemoModel)
    res = webapp.get('/api/s/' + str(x.id) + '/')
    assert res.json['sender'] == fqn(x.sender)


@pytest.mark.django_db
def test_post_single(webapp):
    url = reverse('single')
    res = webapp.post(url, {'sender': fqn(Sender1)})
    assert res.json['sender'] == fqn(Sender1)
    assert DemoModel.objects.get(pk=res.json['id']).sender == Sender1


@pytest.mark.django_db
def test_get_multiple(webapp):
    x = G(DemoMultipleModel, sender=[Sender1, Sender2])
    res = webapp.get('/api/m/' + str(x.id) + '/')
    assert res.json['sender'] == stringify(x.sender)


@pytest.mark.django_db
def test_post_multiple(webapp):
    url = reverse('multiple')

    res = webapp.post(url, {'sender': fqn(Sender1)})
    assert res.json['sender'] == fqn(Sender1)
    assert DemoMultipleModel.objects.get(pk=res.json['id']).sender == [Sender1]

    res = webapp.post(url, {'sender': stringify([Sender1, Sender2])})
    assert res.json['sender'] == stringify([Sender1, Sender2])
    assert DemoMultipleModel.objects.get(pk=res.json['id']).sender == [Sender1, Sender2]

#
