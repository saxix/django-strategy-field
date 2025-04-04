import pytest
from demo.models import DemoModelNoRegistry
from django.core.mail.backends.dummy import EmailBackend


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
    d = DemoModelNoRegistry(instance="django.core.mail.backends.dummy.EmailBackend")
    d.save()
    assert isinstance(d.instance, EmailBackend)


@pytest.mark.django_db
def test_wrong_strategy():
    d = DemoModelNoRegistry(instance="wrong.strategy")
    d.save()
    assert d.instance is None


@pytest.mark.django_db
def test_wrong_type():
    d = DemoModelNoRegistry(instance=1)
    d.save()
    assert d.instance is None
