# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import logging

import pytest
from django.core.exceptions import ValidationError
from django.core.mail.backends.filebased import EmailBackend

from demoproject.demoapp.models import DemoModelNoRegistry

logger = logging.getLogger(__name__)


# @pytest.mark.django_db
# def test_valid_class():
#     d = DemoModelNoRegistry(klass='a.b.c')
#     with pytest.raises(ValidationError):
#         d.clean_fields()


class Dummy:
    pass


@pytest.mark.django_db
def test_no_registry_assign_class():
    d = DemoModelNoRegistry(klass=Dummy)
    d.save()
    assert d.klass == Dummy


@pytest.mark.django_db
def test_no_registry_assign_instance():
    d = DemoModelNoRegistry(instance=Dummy)
    d.save()
    assert isinstance(d.instance, Dummy)


@pytest.mark.django_db
def test_no_registry_assign_string():
    d = DemoModelNoRegistry(instance='django.core.mail.backends.filebased.EmailBackend')
    d.save()
    assert isinstance(d.instance, EmailBackend)
    assert d.instance.open()
