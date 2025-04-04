import logging

import pytest
from demo.models import (
    DemoModelNone,
    DemoMultipleModel,
    Sender1,
    Sender2,
    Strategy,
)
from rest_framework.reverse import reverse
from strategy_field.utils import fqn
from factory.django import DjangoModelFactory

logger = logging.getLogger(__name__)


class DemoModelNoneFactory(DjangoModelFactory):
    class Meta:
        model = DemoModelNone


class DemoMultipleModelFactory(DjangoModelFactory):
    class Meta:
        model = DemoMultipleModel


@pytest.fixture
def record():
    return DemoModelNoneFactory()


@pytest.mark.django_db
def test_get_single(webapp, record):
    x = DemoModelNoneFactory(sender=Strategy)
    res = webapp.get("/api/s/" + str(x.id) + "/")
    assert res.json["sender"] == fqn(x.sender)

    x = DemoModelNoneFactory(sender=None)
    res = webapp.get("/api/s/" + str(x.id) + "/")
    assert res.json["sender"] is None


@pytest.mark.django_db
def test_post_single(webapp):
    url = reverse("single")
    res = webapp.post(url, params={"sender": fqn(Sender1)})
    assert res.json["sender"] == fqn(Sender1)
    assert DemoModelNone.objects.get(pk=res.json["id"]).sender == Sender1

    res = webapp.post(url, params={"sender": ""})
    assert res.json["sender"] is None
    assert DemoModelNone.objects.get(pk=res.json["id"]).sender is None

    res = webapp.post(url, expect_errors=True, params={"sender": fqn(DemoModelNone)})
    assert res.status_code == 400
    assert res.json["sender"] == ["Invalid entry `%s`" % fqn(DemoModelNone)]


@pytest.mark.django_db
def test_get_multiple(webapp):
    x = DemoMultipleModelFactory(sender=[Sender1, Sender2])
    res = webapp.get("/api/m/" + str(x.id) + "/")
    assert res.json["sender"] == sorted(map(fqn, x.sender))

    x = DemoMultipleModelFactory(sender=[])
    res = webapp.get("/api/m/" + str(x.id) + "/")
    assert res.json["sender"] == []

    x = DemoMultipleModelFactory(sender=None)
    res = webapp.get("/api/m/" + str(x.id) + "/")
    assert res.json["sender"] is None


@pytest.mark.django_db
def test_post_multiple(webapp):
    url = reverse("multiple")

    res = webapp.post(url, params={"sender": [fqn(Sender1), fqn(Sender2)]})
    assert res.json["sender"] == [fqn(Sender1), fqn(Sender2)]
    assert DemoMultipleModel.objects.get(pk=res.json["id"]).sender == [Sender1, Sender2]

    res = webapp.post(
        url, expect_errors=True, params={"sender": [fqn(Sender1), fqn(DemoModelNone)]}
    )
    assert res.status_code == 400
    assert res.json["sender"] == ["Invalid entry `%s`" % fqn(DemoModelNone)]
